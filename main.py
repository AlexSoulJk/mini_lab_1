import json
from tkinter import filedialog

import matplotlib

import numexpr as ne
import numpy as np


from functools import partial
from tkinter import *
from tkinter.filedialog import asksaveasfile

from matplotlib import pyplot as plt

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)

matplotlib.use('TkAgg')


# class for entries storage (класс для хранения текстовых полей)
class Entries:
    def __init__(self):
        self.entries_list = []
        self.parent_window = None

    def set_parent_window(self, parent_window):
        self.parent_window = parent_window

    # adding of new entry (добавление нового текстового поля)
    def add_entry(self):
        """

        :rtype: object
        """
        new_entry = Entry(self.parent_window)
        new_entry.icursor(0)
        new_entry.focus()
        new_entry.pack()
        plot_button = self.parent_window.get_button_by_name('plot')
        if plot_button:
            plot_button.pack_forget()
        self.parent_window.add_button('plot', 'Plot', 'plot', hot_key='<Return>')
        self.entries_list.append(new_entry)
    def add_new_entry(self, list_of_functions):
        def clear_entries():
            for i in range(len(self.entries_list)):
                self.entries_list.pop(i).destroy()

        clear_entries()
        for fun in list_of_functions:
            entry = Entry(self.parent_window)
            entry.icursor(0)
            entry.focus()
            entry.insert(0,fun)
            entry.pack()
            self.entries_list.append(entry)





# class for plotting (класс для построения графиков)
class Plotter:
    def __init__(self, x_min=-20, x_max=20, dx=0.01):
        self.x_min = x_min
        self.x_max = x_max
        self.dx = dx
        self._last_plotted_list_of_function = None
        self._last_plotted_figure = None
        self.parent_window = None

    def set_parent_window(self, parent_window):
        self.parent_window = parent_window

    # plotting of graphics (построение графиков функций)
    def plot(self, list_of_function, title='Графики функций', x_label='x', y_label='y', need_legend=True):
        fig = plt.figure()

        x = np.arange(self.x_min, self.x_max, self.dx)

        new_funcs = [f if 'x' in f else 'x/x * ({})'.format(f) for f in list_of_function]

        ax = fig.add_subplot(1, 1, 1)
        for func in new_funcs:
            ax.plot(x, ne.evaluate(func), linewidth=1.5)

        fig.suptitle(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        if need_legend:
            plt.legend(list_of_function)
        self._last_plotted_list_of_function = list_of_function
        self._last_plotted_figure = fig
        return fig


# class for commands storage (класс для хранения команд)
class Commands:
    class State:
        def __init__(self):
            self.list_of_function = []

        def save_state(self):
            tmp_dict = {'list_of_function': self.list_of_function}
            file_out = asksaveasfile(defaultextension=".json")
            if file_out is not None:
                json.dump(tmp_dict, file_out)
            return self
        def open_with(self):
            filename = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
            if filename:
                with open(filename, 'r') as file:
                    data = json.load(file)
            return data['list_of_function']


        def reset_state(self):
            self.list_of_function = []

    def __init__(self):
        self.command_dict = {}
        self.__figure_canvas = None
        self.__navigation_toolbar = None
        self._state = Commands.State()
        self.__empty_entry_counter = 0
        self.parent_window = None

    def set_parent_window(self, parent_window):
        self.parent_window = parent_window

    def add_command(self, name, command):
        self.command_dict[name] = command

    def get_command_by_name(self, command_name):
        return self.command_dict[command_name]

    def __forget_canvas(self):
        if self.__figure_canvas is not None:
            self.__figure_canvas.get_tk_widget().pack_forget()

    def __forget_navigation(self):
        if self.__navigation_toolbar is not None:
            self.__navigation_toolbar.pack_forget()

    def plot(self, *args, **kwargs):
        def is_not_blank(s):
            return bool(s and not s.isspace())

        self._state.reset_state()
        list_of_function = []
        for entry in self.parent_window.entries.entries_list:
            get_func_str = entry.get()
            self._state.list_of_function.append(get_func_str)
            if is_not_blank(get_func_str):
                list_of_function.append(get_func_str)
            else:
                if self.__empty_entry_counter == 0:
                    mw = ModalWindow(self.parent_window, title='Пустая строка', labeltext='Это пример модального окна, '
                                                                                          'возникающий, если ты ввел '
                                                                                          'пустую '
                                                                                          'строку. С этим ничего '
                                                                                          'делать не нужно. '
                                                                                          'Просто нажми OK :)')
                    ok_button = Button(master=mw.top, text='OK', command=mw.cancel)
                    mw.add_button(ok_button)
                    self.__empty_entry_counter = 1
        self.__empty_entry_counter = 0
        figure = self.parent_window.plotter.plot(list_of_function)
        self._state.figure = figure
        self.__forget_canvas()
        self.__figure_canvas = FigureCanvasTkAgg(figure, self.parent_window)
        self.__forget_navigation()
        self.__navigation_toolbar = NavigationToolbar2Tk(self.__figure_canvas, self.parent_window)
        self.__figure_canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        plot_button = self.parent_window.get_button_by_name('plot')
        if plot_button:
            plot_button.pack_forget()


    def add_func(self, *args, **kwargs):
        self.__forget_canvas()
        self.__forget_navigation()
        self.parent_window.entries.add_entry()

    def save_as(self):
        self._state.save_state()
        return self
    def open_with(self):
        data = self._state.open_with()
        self.parent_window.entries.add_new_entry(data)
        self.plot()
    def del_entry_1(self):
        widget = self.parent_window.focus_get()
        if(isinstance(widget, Entry)):
            index = self.parent_window.entries.entries_list.index(widget)
            self.parent_window.entries.entries_list.pop(index).destroy()
    def del_entry_2(self, *args, **kwargs):
        widget = self.parent_window.focus_get()
        if (isinstance(widget, Entry)):
            index_entry = self.parent_window.entries.entries_list.index(widget)
            self._state.list_of_function.pop(index_entry)
            self.parent_window.entries.entries_list.pop(index_entry).destroy()
            self.plot(*args, **kwargs)

    def del_entry_3(self, *args, **kwargs):
        widget = self.parent_window.focus_get()
        if (isinstance(widget, Entry)):
            if len(str(widget.get())):
                mw = ModalWindow(self.parent_window, title='Предупреждение',
                                 labeltext='Вы действительно хотитете удалить строчку с функцией '
                                           + str(widget.get()) + ' ?')
                callback = lambda: mw.cancel() or self.del_con(widget, *args, **kwargs)
                yes_button = Button(master=mw.top, text='Yes', command=callback)
                no_button = Button(master=mw.top, text='No', command=mw.cancel)
                mw.add_button(yes_button)
                mw.add_button(no_button)
            else:
                self.del_con(widget, *args, **kwargs)

    def del_con(self, widget,*args, **kwargs):
        index_entry = self.parent_window.entries.entries_list.index(widget)
        if (len(self._state.list_of_function) > index_entry):
            self._state.list_of_function.pop(index_entry)
        self.parent_window.entries.entries_list.pop(index_entry).destroy()
        self.plot(*args, **kwargs)



# class for buttons storage (класс для хранения кнопок)
class Buttons:
    def __init__(self):
        self.buttons = {}
        self.parent_window = None

    def set_parent_window(self, parent_window):
        self.parent_window = parent_window

    def add_button(self, name, text, command):
        new_button = Button(master=self.parent_window, text=text, command=command)
        self.buttons[name] = new_button
        return new_button

    def delete_button(self, name):
        button = self.buttons.get(name)
        if button:
            button.pack_forget()


# class for generate modal windows (класс для генерации модальных окон)
class ModalWindow:
    def __init__(self, parent, title, labeltext=''):
        self.buttons = []
        self.top = Toplevel(parent)
        self.top.transient(parent)
        self.top.grab_set()
        if len(title) > 0:
            self.top.title(title)
        if len(labeltext) == 0:
            labeltext = 'Default text'
        Label(self.top, text=labeltext).pack()

    def add_button(self, button):
        self.buttons.append(button)
        button.pack(pady=5)

    def cancel(self):
        self.top.destroy()


# app class (класс приложения)
class App(Tk):
    def __init__(self, buttons, plotter, commands, entries):
        super().__init__()
        self.buttons = buttons
        self.plotter = plotter
        self.commands = commands
        self.entries = entries
        self.entries.set_parent_window(self)
        self.plotter.set_parent_window(self)
        self.commands.set_parent_window(self)
        self.buttons.set_parent_window(self)
        self.geometry("640x480")
    def add_button(self, name, text, command_name, *args, **kwargs):
        hot_key = kwargs.get('hot_key')
        if hot_key:
            kwargs.pop('hot_key')
        callback = partial(self.commands.get_command_by_name(command_name), *args, **kwargs)
        new_button = self.buttons.add_button(name=name, text=text, command=callback)
        if hot_key:
            self.bind(hot_key, callback)
        new_button.pack(fill=BOTH)

    def get_button_by_name(self, name):
        return self.buttons.buttons.get(name)

    def create_menu(self):
        menu = Menu(self)
        self.config(menu=menu)

        file_menu = Menu(menu)
        file_menu.add_command(label="Save as...", command=self.commands.get_command_by_name('save_as'))
        file_menu.add_command(label="Open with...", command=self.commands.get_command_by_name('open_with'))
        menu.add_cascade(label="File", menu=file_menu)




if __name__ == "__main__":
    # init buttons (создаем кнопки)
    buttons_main = Buttons()
    # init plotter (создаем отрисовщик графиков)
    plotter_main = Plotter()
    # init commands for executing on buttons or hot keys press
    # (создаем команды, которые выполняются при нажатии кнопок или горячих клавиш)
    commands_main = Commands()
    # init entries (создаем текстовые поля)
    entries_main = Entries()
    # command's registration (регистрация команд)
    commands_main.add_command('plot', commands_main.plot)
    commands_main.add_command('add_func', commands_main.add_func)
    commands_main.add_command('save_as', commands_main.save_as)
    commands_main.add_command('open_with', commands_main.open_with)
    commands_main.add_command('del_entry_1',commands_main.del_entry_1)
    # init app (создаем экземпляр приложения)
    app = App(buttons_main, plotter_main, commands_main, entries_main)
    # init add func button (добавляем кнопку добавления новой функции)
    app.add_button('add_func', 'Добавить функцию', 'add_func', hot_key='<Control-a>')
    app.add_button('del_entry_1', 'Удалить функцию', 'del_entry_1')
    app.bind("<Control-o>", commands_main.del_entry_2)
    app.bind("<Control-r>", commands_main.del_entry_3)
    # init first entry (создаем первое поле ввода)
    entries_main.add_entry()
    app.create_menu()
    # добавил комментарий для коммита
    # application launch (запуск "вечного" цикла приложеня)
    app.mainloop()
