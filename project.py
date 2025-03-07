import os
import whisper
import tkinter as tk
from tkinter import filedialog, messagebox
import re
import threading
import pyaudio
import wave
from transformers import BartTokenizer, BartForConditionalGeneration
from fpdf import FPDF

os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"
model = whisper.load_model("base")
tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
bart_model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

if not os.path.exists("recordings"):
    os.makedirs("recordings")

def abstractive_summary_bart(text):
    inputs = tokenizer([text], max_length=1024, return_tensors='pt', truncation=True)
    
    summary_ids = bart_model.generate(
        inputs['input_ids'], 
        num_beams=6,  
        max_length=150,  
        early_stopping=True
    )
    
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

def extract_department_tasks(meeting_text, departments):
    tasks = {dept: [] for dept in departments}
    
    sentences = meeting_text.split('.')
    
    task_keywords = ['responsible for', 'needs to', 'should', 'must', 'required to', 'have to', 'prioritize', 'key']
    
    for sentence in sentences:
        for dept in departments:
            if dept.lower() in sentence.lower():
                for keyword in task_keywords:
                    if keyword in sentence.lower():
                        cleaned_task = re.sub(r'(responsible for|needs to|should|must|required to|have to|prioritize|key)', '', sentence, flags=re.IGNORECASE).strip()
                        
                        cleaned_task = re.sub(r'^\s*(first|meanwhile|then|next|the|this time|they will be|let’s|the sales team|a detailed plan)', '', cleaned_task, flags=re.IGNORECASE)
                        
                        cleaned_task = cleaned_task.strip(',').strip()
                        
                        task_parts = re.split(r',|and', cleaned_task)
                        
                        for part in task_parts:
                            task = part.strip()
                            if task:  
                                tasks[dept].append(task.capitalize())  
                        break  
    return tasks

import pywhatkit as kit
import pywhatkit as kit
from tkinter import simpledialog, messagebox

def generate_pdf_report(meeting_name, summary, tasks):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"Meeting Name: {meeting_name}", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt="Summary:", ln=True, align='L')
    pdf.multi_cell(0, 10, txt=summary, align='L')
    pdf.ln(10)
    
    pdf.cell(200, 10, txt="Department-wise Tasks:", ln=True, align='L')
    for dept, task_list in tasks.items():
        pdf.ln(5)
        pdf.cell(200, 10, txt=f"{dept}:", ln=True, align='L')
        for i, task in enumerate(task_list, 1):
            pdf.multi_cell(0, 10, txt=f"  {i}. {task}", align='L')

    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if file_path:
        pdf.output(file_path)
        messagebox.showinfo("PDF Report", f"Report saved as {file_path}")

    send_tasks = messagebox.askyesno("Send Tasks", "Do you want to send the tasks to departments via WhatsApp?")
    
    if send_tasks:
        for dept, task_list in tasks.items():
            dept_number = simpledialog.askstring("Input", f"Enter WhatsApp number for {dept} (in +91 format):")
            if dept_number:
                task_message = f"Tasks for {dept}:\n"
                for i, task in enumerate(task_list, 1):
                    task_message += f"  {i}. {task}\n"
                
                try:
                    import time
                    current_time = time.localtime()
                    send_hour = current_time.tm_hour
                    send_minute = current_time.tm_min + 1  # Adding one minute for sending the message
                    
                    kit.sendwhatmsg_instantly(dept_number, task_message)
                    messagebox.showinfo("Message Sent", f"Tasks sent to {dept}!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to send message: {e}")

class TranscriberApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Meeting Transcriber App")
        self.geometry("600x400")
        self.configure(bg="#f0f0f0")
        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self, bg="#ffffff", padx=20, pady=20)
        frame.pack(expand=True, fill='both', padx=10, pady=10)

        tk.Label(frame, text="Meeting Transcriber App", font=("Helvetica", 16, "bold"), bg="#ffffff").pack(pady=10)

        input_frame = tk.Frame(frame, bg="#ffffff", padx=10, pady=10)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Enter Meeting Name:", font=("Helvetica", 12), bg="#ffffff").grid(row=0, column=0, sticky='w', pady=5)
        self.meeting_name_entry = tk.Entry(input_frame, width=40, font=("Helvetica", 12))
        self.meeting_name_entry.grid(row=0, column=1, pady=5)

        tk.Label(input_frame, text="Enter Departments Attending:", font=("Helvetica", 12), bg="#ffffff").grid(row=1, column=0, sticky='w', pady=5)
        self.departments_entry = tk.Entry(input_frame, width=40, font=("Helvetica", 12))
        self.departments_entry.grid(row=1, column=1, pady=5)

        mode_frame = tk.Frame(frame, bg="#ffffff", padx=10, pady=10)
        mode_frame.pack(pady=10)

        tk.Label(mode_frame, text="Select Mode of Audio Input:", font=("Helvetica", 12), bg="#ffffff").pack(anchor='w', pady=5)
        self.mode_var = tk.StringVar(value="Audio")
        tk.Radiobutton(mode_frame, text="Audio", variable=self.mode_var, value="Audio", font=("Helvetica", 12), bg="#ffffff").pack(anchor='w')
        tk.Radiobutton(mode_frame, text="Video", variable=self.mode_var, value="Video", font=("Helvetica", 12), bg="#ffffff").pack(anchor='w')
        tk.Radiobutton(mode_frame, text="Live Recording", variable=self.mode_var, value="Live Recording", font=("Helvetica", 12), bg="#ffffff").pack(anchor='w')

        tk.Button(frame, text="Start Process", command=self.start_process, font=("Helvetica", 12), bg="#4caf50", fg="#ffffff").pack(pady=20)

    def start_process(self):
        meeting_name = self.meeting_name_entry.get()
        departments = self.departments_entry.get().split(',')
        mode = self.mode_var.get()

        if not meeting_name or not departments:
            messagebox.showerror("Error", "Please enter both meeting name and departments.")
            return

        if mode == "Audio":
            file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3;*.wav")])
        elif mode == "Video":
            file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.mov")])
        else:
            LiveRecordingWindow(self)
            return

        if file_path:
            transcript = self.transcribe(file_path)
            summary = abstractive_summary_bart(transcript)
            tasks = extract_department_tasks(transcript, departments)

            report = f"Meeting Name: {meeting_name}\n\nSummary: {summary}\n\nDepartment-wise Tasks:\n"
            for dept, task_list in tasks.items():
                report += f"\n{dept}:\n"
                for i, task in enumerate(task_list, 1):
                    report += f"  {i}. {task}\n"

            messagebox.showinfo("Final Report", report)
            generate_pdf_report(meeting_name, summary, tasks)

    def transcribe(self, file_path):
        result = model.transcribe(file_path, task="translate")
        return result["text"]

class LiveRecordingWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Live Recording")
        self.geometry("300x200")
        self.recording = False
        self.create_widgets()
        self.frames = []
        self.stream = None
        self.p = pyaudio.PyAudio()
        self.chunk = 1024
        self.sample_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.recording_thread = None

    def create_widgets(self):
        self.start_button = tk.Button(self, text="Start Recording", command=self.start_recording, font=("Helvetica", 12), bg="#f44336", fg="#ffffff")
        self.start_button.pack(pady=10)
        self.stop_button = tk.Button(self, text="Stop Recording", command=self.stop_recording, font=("Helvetica", 12), bg="#f44336", fg="#ffffff")
        self.stop_button.pack(pady=10)
        self.stop_button.config(state=tk.DISABLED)

    def start_recording(self):
        self.recording = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.stream = self.p.open(format=self.sample_format, channels=self.channels, rate=self.rate, input=True, frames_per_buffer=self.chunk)
        self.frames = []
        self.recording_thread = threading.Thread(target=self.record_audio)
        self.recording_thread.start()

    def record_audio(self):
        while self.recording:
            data = self.stream.read(self.chunk)
            self.frames.append(data)

    def stop_recording(self):
        self.recording = False
        self.recording_thread.join()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

        confirm = messagebox.askyesno("Confirmation", "Do you want to transcribe the recording and generate the report?")
        if confirm:
            audio_data = b''.join(self.frames)

            temp_audio_path = "temp_recording.wav"
            with wave.open(temp_audio_path, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.p.get_sample_size(self.sample_format))
                wf.setframerate(self.rate)
                wf.writeframes(audio_data)

            transcript = app.transcribe(temp_audio_path)
            departments = app.departments_entry.get().split(',')
            summary = abstractive_summary_bart(transcript)
            tasks = extract_department_tasks(transcript, departments)

            report = f"Meeting Name: {app.meeting_name_entry.get()}\n\nSummary: {summary}\n\nDepartment-wise Tasks:\n"
            for dept, task_list in tasks.items():
                report += f"\n{dept}:\n"
                for i, task in enumerate(task_list, 1):
                    report += f"  {i}. {task}\n"

            messagebox.showinfo("Final Report", report)

            generate_pdf_report(app.meeting_name_entry.get(), summary, tasks)

            os.remove(temp_audio_path)  

if __name__ == "__main__":
    app = TranscriberApp()
    app.mainloop()
