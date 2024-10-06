import random
from kivy.uix.screenmanager import SlideTransition
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.base import EventLoop
from kivy.utils import platform

# Renk Tanımları
BACKGROUND_COLOR = (0.1, 0.1, 0.1, 1)  # Koyu gri
BUTTON_COLOR = (0.1, 0.6, 0.9, 1)  # Mavi
BUTTON_HOVER_COLOR = (0.1, 0.8, 1, 1)  # Mavi (hover durumu)
TEXT_COLOR = (1, 1, 1, 1)  # Beyaz
CORRECT_COLOR = (0.2, 1, 0.2, 1)  # Yeşil
INCORRECT_COLOR = (1, 0.2, 0.2, 1)  # Kırmızı

# Kelimeler
WORDS = [
    {"word": "a", "meaning": "bir", "example": "She has a cat."},
    {"word": "ability", "meaning": "kabiliyet, yetenek, beceri", "example": "She has the ability to learn quickly."},
    {"word": "able", "meaning": "yapabilmek, yapabilen", "example": "He is able to solve complex problems."},
    {"word": "about", "meaning": "hakkında, ilgili, konusunda", "example": "We talked about the project."},
    {"word": "above", "meaning": "yukarıda", "example": "The plane flew above the clouds."},
    {"word": "accept", "meaning": "kabul etmek", "example": "Please accept my apology."},
    {"word": "according", "meaning": "göre", "example": "According to the report, sales have increased."},
    {"word": "account", "meaning": "hesap, açıklama", "example": "I need to check my bank account."},
    {"word": "across", "meaning": "karşısında", "example": "The park is across the street."}
]

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        learn_button = CustomButton(text="Learn", size_hint=(1, 0.25), pos_hint={'center_x': 0.5, 'center_y': 0.65})
        quiz_button = CustomButton(text="Quiz", size_hint=(1, 0.25), pos_hint={'center_x': 0.5, 'center_y': 0.35})

        learn_button.bind(on_press=self.go_to_learn)
        quiz_button.bind(on_press=self.go_to_quiz)

        layout.add_widget(learn_button)
        layout.add_widget(quiz_button)

        self.add_widget(layout)

    def go_to_learn(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'learn'

    def go_to_quiz(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'quiz'

class CustomButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''  # Normal arka planı kaldır
        self.background_color = BUTTON_COLOR  # Varsayılan arka plan rengini ayarla

    def on_hover(self, *args):
        self.background_color = BUTTON_HOVER_COLOR  # Hover durumu için arka plan rengini değiştir

    def on_leave(self, *args):
        self.background_color = BUTTON_COLOR  # Normal duruma döndür


class LearnScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.words = WORDS.copy()  # Kelimelerin kopyasını al
        random.shuffle(self.words)  # Kelimeleri karıştır
        self.current_index = 0

        self.layout = FloatLayout()

        self.word_label = Label(text='', font_size=125, color=TEXT_COLOR, pos_hint={'center_x': 0.5, 'center_y': 0.75},
                                text_size=(Window.width * 0.9, None), halign="center", valign="middle")

        self.meaning_label = Label(text='', font_size=60, color=TEXT_COLOR,
                                   pos_hint={'center_x': 0.5, 'center_y': 0.55},
                                   text_size=(Window.width * 0.9, None), halign="center", valign="middle")

        self.example_label = Label(text='', font_size=60, color=TEXT_COLOR,
                                   pos_hint={'center_x': 0.5, 'center_y': 0.35},
                                   text_size=(Window.width * 0.9, None), halign="center", valign="middle")

        self.next_button = CustomButton(text='Next', size_hint=(1, 0.1), pos_hint={'center_x': 0.5, 'center_y': 0.15})

        self.layout.add_widget(self.word_label)
        self.layout.add_widget(self.meaning_label)
        self.layout.add_widget(self.example_label)
        self.layout.add_widget(self.next_button)

        self.next_button.bind(on_press=self.show_next_word)

        self.add_widget(self.layout)
        self.show_next_word()

    def show_next_word(self, *args):
        if self.words:  # Eğer kelimeler varsa
            word = self.words[self.current_index]
            self.word_label.text = word['word']
            self.meaning_label.text = word['meaning']
            self.example_label.text = word['example']

            self.current_index += 1
            if self.current_index >= len(self.words):
                self.current_index = 0  # Kelime listesinin sonuna geldiğinde sıfırla
                random.shuffle(self.words)  # Kelimeleri yeniden karıştır
        else:
            self.word_label.text = "No words available."

    def go_back(self, *args):
        self.manager.current = 'main'  # Ana ekrana geri dön


class QuizScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.words = WORDS
        self.score = 0
        self.current_question = None
        self.current_word_indices = list(range(len(self.words)))  # Kelimelerin indekslerini tut
        random.shuffle(self.current_word_indices)  # İndeksleri karıştır
        self.current_index = 0  # Şu anki kelime indeksi

        self.layout = FloatLayout()

        self.question_label = Label(text='', font_size=130, color=TEXT_COLOR,
                                    pos_hint={'center_x': 0.5, 'center_y': 0.7})
        self.layout.add_widget(self.question_label)

        self.option_buttons = []
        for i in range(3):
            button = CustomButton(text='', size_hint=(1, 0.1), pos_hint={'center_x': 0.5, 'y': 0.35 - (i * 0.13)})
            button.bind(on_press=self.check_answer)
            self.option_buttons.append(button)
            self.layout.add_widget(button)

        self.score_label = Label(
            text='Score: 0',
            font_size=55,
            color=TEXT_COLOR,
            size_hint=(0.2, 0.1),  # Boyutlandırmayı ekranla orantılı yapmak için size_hint kullanıyoruz
            pos_hint={'right': 0.95, 'top': 1}  # Sağ üst köşe için pos_hint ayarları
        )
        self.layout.add_widget(self.score_label)
        self.add_widget(self.layout)
        self.show_new_question()

    def show_new_question(self):
        if self.current_index >= len(self.current_word_indices):  # Eğer tüm kelimeler sorulduysa
            self.current_index = 0
            random.shuffle(self.current_word_indices)  # Yeniden karıştır

        word_index = self.current_word_indices[self.current_index]  # Karıştırılmış kelime listesinden kelime al
        self.current_question = self.words[word_index]
        self.question_label.text = self.current_question['word']
        random_words = random.sample(self.words, 2)  # Sadece 2 rastgele kelime al
        options = random_words + [self.current_question]
        random.shuffle(options)  # Seçenekleri karıştır

        for i, button in enumerate(self.option_buttons):
            button.text = options[i]['meaning']  # Her bir düğmeye anlamı ata

        self.current_index += 1

    def check_answer(self, instance):
        selected_meaning = instance.text  # Seçilen butonun metnini al
        correct_meaning = self.current_question['meaning']

        for button in self.option_buttons:
            button.unbind(on_press=self.check_answer)  # Tüm butonların olayı iptal et
            if button.text == correct_meaning:
                button.background_color = CORRECT_COLOR  # Doğru butonu yeşil yap
            else:
                button.background_color = INCORRECT_COLOR  # Yanlış butonu kırmızı yap

        if selected_meaning == correct_meaning:
            self.score += 1  # Doğru cevap verildiğinde puanı artır
        self.score_label.text = f'Score: {self.score}'  # Puanı güncelle

        Clock.schedule_once(self.show_new_question, 1.5)  # 1.5 saniye sonra yeni soruya geç

    def go_back(self, *args):
        self.manager.current = 'main'  # Ana ekrana geri dön


class VocabularyApp(App):
    def build(self):
        Window.clearcolor = BACKGROUND_COLOR
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(LearnScreen(name='learn'))
        sm.add_widget(QuizScreen(name='quiz'))

        if platform == 'android':
            EventLoop.window.bind(on_keyboard=self.on_back_button)

        return sm

    def on_back_button(self, window, key, *args):
        if key == 27:  # Android geri butonu keycode'u 27'dir
            if self.root.current != 'main':
                self.root.current = 'main'  # Ana ekrana geri dön
                return True  # Varsayılan davranışı önle (uygulamadan çıkma)
            return False  # Varsayılan davranışın gerçekleşmesine izin ver (uygulamadan çıkma)

if __name__ == '__main__':
    VocabularyApp().run()
