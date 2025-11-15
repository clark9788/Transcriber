"""Tkinter GUI entry point for the Medical Transcriber application."""

from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Optional

from audio_recorder import AudioRecorder
from file_manager import (
    generate_filename,
    list_transcriptions,
    load_transcription,
    save_transcription,
    secure_delete,
)
from gcloud_transcriber import upload_and_transcribe
from template_manager import apply_template, load_templates
from transcription_cleaner import remove_filler_words


class TranscriberApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Medical Transcriber")
        self.geometry("1100x700")

        self.recorder = AudioRecorder()
        self.current_recording: Optional[Path] = None
        self.current_transcription_file: Optional[Path] = None
        self.templates = load_templates()
        self._transcribe_thread: Optional[threading.Thread] = None
        self.file_listing: list[Path] = []

        self._build_ui()
        self.refresh_file_list()

    # UI setup -----------------------------------------------------------------
    def _build_ui(self) -> None:
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Patient Name").grid(row=0, column=0, sticky="w")
        self.patient_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.patient_var, width=25).grid(row=0, column=1, padx=5)

        ttk.Label(top, text="DOB (YYYYMMDD)").grid(row=0, column=2, sticky="w")
        self.dob_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.dob_var, width=15).grid(row=0, column=3, padx=5)

        ttk.Label(top, text="Template").grid(row=0, column=4, sticky="w")
        self.template_var = tk.StringVar()
        template_choices = list(self.templates.keys())
        self.template_combo = ttk.Combobox(top, textvariable=self.template_var, values=template_choices, state="readonly")
        self.template_combo.grid(row=0, column=5, padx=5)

        self.status_var = tk.StringVar(value="Idle")
        ttk.Label(top, textvariable=self.status_var).grid(row=0, column=6, padx=5)

        button_row = ttk.Frame(top)
        button_row.grid(row=1, column=0, columnspan=7, pady=(10, 0))

        ttk.Button(button_row, text="Record", command=self.start_record).grid(row=0, column=0, padx=5)
        ttk.Button(button_row, text="Stop", command=self.stop_record).grid(row=0, column=1, padx=5)
        ttk.Button(button_row, text="Send to Google", command=self.trigger_transcription).grid(row=0, column=2, padx=5)
        ttk.Button(button_row, text="Delete Recording", command=self.delete_recording).grid(row=0, column=3, padx=5)
        ttk.Button(button_row, text="Save", command=self.save_current_transcription).grid(row=0, column=4, padx=5)
        ttk.Button(button_row, text="Clean Transcription", command=self.clean_transcription).grid(row=0, column=5, padx=5)
        ttk.Button(button_row, text="Delete Transcription", command=self.delete_transcription).grid(row=0, column=6, padx=5)

        body = ttk.Frame(self, padding=10)
        body.pack(fill="both", expand=True)

        left = ttk.Frame(body, width=250)
        left.pack(side="left", fill="y")
        ttk.Label(left, text="Transcriptions").pack(anchor="w")
        self.file_listbox = tk.Listbox(left)
        self.file_listbox.pack(fill="both", expand=True, pady=(5, 0))
        self.file_listbox.bind("<<ListboxSelect>>", self.load_selected_file)

        right = ttk.Frame(body)
        right.pack(side="right", fill="both", expand=True)
        ttk.Label(right, text="Transcription Editor").pack(anchor="w")
        self.text_editor = tk.Text(right, wrap="word")
        self.text_editor.pack(fill="both", expand=True, pady=(5, 0))

    # Status helpers -----------------------------------------------------------
    def set_status(self, message: str) -> None:
        self.after(0, lambda: self.status_var.set(message))

    # Recording controls -------------------------------------------------------
    def start_record(self) -> None:
        try:
            self.current_recording = self.recorder.start()
            self.set_status(f"Recording → {self.current_recording.name}")
        except Exception as exc:  # pragma: no cover - UI interaction
            messagebox.showerror("Recording Error", str(exc))

    def stop_record(self) -> None:
        recording = self.recorder.stop()
        if recording:
            self.set_status("Recording stopped")

    def delete_recording(self) -> None:
        if not self.current_recording:
            return
        secure_delete(self.current_recording, self.patient_var.get())
        self.current_recording = None
        self.set_status("Recording deleted")

    # Transcription workflow ---------------------------------------------------
    def trigger_transcription(self) -> None:
        if self._transcribe_thread and self._transcribe_thread.is_alive():
            messagebox.showinfo("In Progress", "Transcription already running.")
            return
        if not self.current_recording or not self.current_recording.exists():
            messagebox.showerror("No recording", "Please record audio first.")
            return
        patient = self.patient_var.get().strip()
        if not patient:
            messagebox.showerror("Missing info", "Patient name is required before transcription.")
            return

        self._transcribe_thread = threading.Thread(
            target=self._run_transcription,
            args=(self.current_recording, patient),
            daemon=True,
        )
        self._transcribe_thread.start()

    def _run_transcription(self, recording: Path, patient: str) -> None:
        try:
            transcript = upload_and_transcribe(recording, patient, self.set_status)
        except Exception as exc:  # pragma: no cover - API failure
            self.after(0, lambda: messagebox.showerror("Transcription Error", str(exc)))
            self.set_status("Transcription failed")
            return

        template_name = self.template_var.get()
        template = self.templates.get(template_name)
        context = {"PATIENT": patient, "DOB": self.dob_var.get().strip()}
        if template:
            final_text = apply_template(template, transcript, context)
        else:
            final_text = transcript

        def update_editor() -> None:
            self.text_editor.delete("1.0", tk.END)
            self.text_editor.insert(tk.END, final_text)
            self.current_transcription_file = None  # New transcription, not from file
            self.set_status("Transcription ready")

        self.after(0, update_editor)

    # File management ----------------------------------------------------------
    def save_current_transcription(self) -> None:
        patient = self.patient_var.get().strip()
        dob = self.dob_var.get().strip()
        if not patient or not dob:
            messagebox.showerror("Missing info", "Patient name and DOB are required.")
            return
        content = self.text_editor.get("1.0", tk.END).strip()
        if not content:
            messagebox.showerror("Empty", "Transcription text is empty.")
            return
        path = generate_filename(patient, dob)
        save_transcription(path, content)
        self.current_transcription_file = path  # Track newly saved file
        self.refresh_file_list()
        self.after(0, lambda: self.set_status(f"Saved {path.name}"))
        # Securely delete recording post-save
        if self.current_recording:
            secure_delete(self.current_recording, patient)
            self.current_recording = None

    def refresh_file_list(self) -> None:
        self.file_listbox.delete(0, tk.END)
        self.file_listing = list_transcriptions()
        for path in self.file_listing:
            self.file_listbox.insert(tk.END, path.name)

    def load_selected_file(self, _event=None) -> None:
        selection = self.file_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        try:
            path = self.file_listing[index]
        except IndexError:
            return
        content = load_transcription(path)
        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert(tk.END, content)
        self.current_transcription_file = path  # Track loaded file
        self.set_status(f"Loaded {path.name}")

    def clean_transcription(self) -> None:
        """Remove filler words from the current transcription text."""
        content = self.text_editor.get("1.0", tk.END)
        if not content.strip():
            messagebox.showinfo("Empty", "No transcription text to clean.")
            return
        
        cleaned = remove_filler_words(content)
        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert(tk.END, cleaned)
        self.set_status("Transcription cleaned")

    def delete_transcription(self) -> None:
        """Securely delete the currently loaded transcription file."""
        if not self.current_transcription_file:
            messagebox.showinfo("No file", "No transcription file is currently loaded.")
            return
        
        # Confirm deletion
        filename = self.current_transcription_file.name
        if not messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to permanently delete '{filename}'?\n\n"
            "This action cannot be undone.",
        ):
            return
        
        patient = self.patient_var.get().strip() or "unknown"
        secure_delete(self.current_transcription_file, patient)
        self.current_transcription_file = None
        
        # Clear editor
        self.text_editor.delete("1.0", tk.END)
        
        # Refresh file list
        self.refresh_file_list()
        self.set_status(f"Deleted {filename}")


def main() -> None:
    app = TranscriberApp()
    app.mainloop()


if __name__ == "__main__":
    main()
