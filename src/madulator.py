import pyaudio as pa
from src.generator import Generator
from src.samples import Samples
from src.waveform import Waveform
from src.spectrogram import *

BITRATE = 11025


class Madulator(pg.GraphicsView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generator = Generator(1)
        self.setup_layout()
        self.setup_waveform()
        self.setup_spectrograph()
        self.samples = Samples(self.waveform.data_available, self.spectrograph.data_available)
        self.samples.set_expression(self.generator.random_function())
        self.setup_instructions()
        self.layout.nextRow()
        self.layout.nextRow()
        self.setup_editor()
        self.setup_pyaudio()
        self.stream.start_stream()

    def setup_pyaudio(self) -> None:
        self.pa = pa.PyAudio()
        self.stream = self.pa.open(format = pa.get_format_from_width(1),
            channels = 1,
            rate = BITRATE,
            output = True,
            stream_callback=self.samples.pyaudio_callback)

    def keyPressEvent(self, ev: QtGui.QKeyEvent) -> None:
        key = ev.key()
        if key == QtCore.Qt.Key.Key_Escape:
            self.stream.stop_stream()
            self.stream.close()
            self.pa.terminate()
            QtCore.QCoreApplication.quit()
        elif key == QtCore.Qt.Key.Key_R:
            self.stream.stop_stream()
            self.samples.set_expression(self.generator.random_function())
            self.stream.start_stream()
            exp = self.samples.get_expression()
            self.editor_text.setText(exp.html_tree([exp, exp.left]))
        elif key == QtCore.Qt.Key.Key_Space:
            self.stream.stop_stream()
            # Save editor expression to samples
            exp = self.samples.get_expression()
            self.samples.set_expression(exp)
            self.stream.start_stream()
            self.editor_text.setText(str(exp))

    def setup_layout(self) -> None:
        self.layout = pg.GraphicsLayout(border=(100,100,100))
        self.setCentralItem(self.layout)
        self.show()
        self.setWindowTitle('MADulator')
        self.resize(1024, 720)

    def setup_waveform(self) -> None:
        self.waveform = Waveform()
        self.layout.addItem(self.waveform)

    def setup_spectrograph(self) -> None:
        self.spectrograph = SpectrogramWidget(BITRATE)
        self.layout.addItem(self.spectrograph)

    def setup_instructions(self) -> None:
        text = '''
        <h1>MADulator</h1>
        <p>Explore randomly generated sound functions.</p>
        <p><strong>Keys:</strong></p>
        <ul>
        <li>[r] generate random function</li>
        <li>[up] [left] [right] navigate function</li>
        <li>[v] replace expression with value (integer)</li>
        <li>[t] replace expression with variable</li>
        <li>[+] replace expression with addition</li>
        <li>[-] replace expression with subtraction</li>
        <li>[*] replace expression with multiplication</li>
        <li>[/] replace expression with integer division</li>
        <li>[%] replace expression with modulo</li>
        <li>[&] replace expression with bitwise AND</li>
        <li>[|] replace expression with bitwise OR</li>
        <li>[^] replace expression with bitwise XOR</li>
        <li>[space] apply changes / restart playback</li>
        <li>[esc] exit program</li>
        </ul>
        '''
        self.layout.addLabel(text, rowspan=3)

    def setup_editor(self) -> None:
        self.editor_text = pg.LabelItem(name='Test', colspan=2)
        self.layout.addItem(self.editor_text)
        self.editor_text.setText('Function here')