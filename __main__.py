import game
import tkinter
import tkinter.filedialog
import tkinter.messagebox
import traceback


def prompt_file():
    top = tkinter.Tk()
    top.withdraw()
    file_name = tkinter.filedialog.askopenfilename(parent=top, initialdir="levels")
    top.wm_deiconify() # Fix to bring the game back up instead of having it minimised
    top.destroy()
    return file_name

def show_error(message: str):
    top = tkinter.Tk()
    top.withdraw()
    tkinter.messagebox.showerror("Error", message)
    top.wm_deiconify()
    top.destroy()

def main() -> int:
    level_filename: str = prompt_file()
    if not level_filename.endswith('.py'):
        show_error("Please open a valid Python script file (.py).")
        return 1
    
    try:
        with open(level_filename, 'r') as level_file, open(level_filename[:-2] + 'geom', 'r', encoding='utf-8') as geometry_file:
            g = game.Game(800, 600, "Ferris the Cat", level_file, geometry_file)
            g.start()
        return 0
    except Exception:
        show_error("Ferris has witnessed and error and has to run away!\n\n" + traceback.format_exc())
        g.quit = True
        return 1

if __name__ == '__main__':
    main()
