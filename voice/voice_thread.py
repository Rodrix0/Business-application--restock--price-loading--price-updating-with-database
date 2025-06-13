from PyQt5.QtCore import QThread, pyqtSignal
import speech_recognition as sr

class VoiceRecognitionThread(QThread):
    # Definir una señal para enviar el texto reconocido de vuelta a la interfaz
    result_ready = pyqtSignal(str)
    
    def __init__(self, campo_seleccionado, parent=None):
        super(VoiceRecognitionThread, self).__init__(parent)
        self.campo_seleccionado = campo_seleccionado

    def run(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            # Reconocimiento de voz en un hilo separado
            audio = recognizer.listen(source)

            try:
                # Convertir el audio a texto
                texto = recognizer.recognize_google(audio, language="es-ES")
                self.result_ready.emit(texto)  # Emitir el resultado
            except sr.UnknownValueError:
                self.result_ready.emit("No se pudo reconocer la voz.")
            except sr.RequestError as e:
                self.result_ready.emit(f"Error en el reconocimiento de voz: {e}") 