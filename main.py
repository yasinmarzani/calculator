from tkinter import *


def clear_display():
    # Clear the entire display.
    display.delete(0, END)


def is_operator(value):
    # Check whether the given character is an operator.
    return value in ("+", "−", "×", "÷")


def can_insert_decimal():
    current = display.get()

    # Extract the last number from the expression.
    last_number = current

    for operator in ("+", "−", "×", "÷"):
        last_number = last_number.replace(operator, " ")

    last_number = last_number.split()[-1] if last_number.split() else ""

    # Allow a decimal point only if the last number has none.
    return "." not in last_number


def handle_display(value):
    global result_shown

    # Start a new expression when a number is entered after a result.
    if result_shown and value in (
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        ".",
    ):
        clear_display()

    # Handle clear buttons.
    if value in ("C", "CE"):
        clear_display()
        result_shown = False

    # Remove the last character.
    elif value == "⌫":
        current = display.get()

        if current:
            display.delete(len(current) - 1, END)

        result_shown = False

    # Calculate the expression.
    elif value == "=":
        calculate()

    # Change the sign of the last number.
    elif value == "±":
        toggle_sign()
        result_shown = False

    else:
        current = display.get()

        # Replace the previous operator if another operator is entered.
        if is_operator(value) and current:
            if is_operator(current[-1]):
                display.delete(len(current) - 1, END)

        # Prevent multiple leading zeros.
        if value == "0":
            if not current or is_operator(current[-1]):
                display.insert(END, "0")
                result_shown = False
                return
        
            if current.endswith("0"):
                if len(current) == 1 or is_operator(current[-2]):
                    return
        
        # Replace a leading zero with the next digit.
        if value in "123456789" and current.endswith("0"):
            if len(current) == 1 or is_operator(current[-2]):
                display.delete(len(current) - 1, END)

        # Handle decimal point insertion.
        if value == ".":
            if not current or is_operator(current[-1]):
                display.insert(END, "0.")
            elif can_insert_decimal():
                display.insert(END, ".")
        else:
            display.insert(END, value)

        result_shown = False


def toggle_sign():
    current = display.get()

    if not current or current == "0":
        return

    # Find the position of the last operator.
    last_operator = max(
        current.rfind("+"),
        current.rfind("−"),
        current.rfind("×"),
        current.rfind("÷"),
    )

    # Locate the beginning of the last number.
    start = last_operator + 1

    # Remove the negative sign or insert one.
    if start < len(current) and current[start] == "-":
        display.delete(start, start + 1)
    else:
        display.insert(start, "-")


def calculate():
    global result_shown

    expression = display.get()

    # Convert display operators into Python operators.
    expression = expression.replace("×", "*")
    expression = expression.replace("÷", "/")
    expression = expression.replace("−", "-")

    try:
        # Evaluate the mathematical expression.
        result = eval(expression)

        clear_display()
        display.insert(END, result)
        result_shown = True

    except (SyntaxError, ZeroDivisionError, NameError, TypeError):
        # Display an error if the expression is invalid.
        clear_display()
        display.insert(END, "ERROR")
        result_shown = True


# Create the main window.
window = Tk()
window.title("Calculator")
window.geometry("320x500")
window.minsize(height=250, width=160)

result_shown = False

# Main frame containing the display and buttons.
main_frame = Frame(window, padx=3, pady=3)
main_frame.pack(fill="both", expand=True)

# Calculator display.
display = Entry(main_frame, font=("Arial", 36), justify="right")
display.pack(fill="x", ipady=28)

# Frame containing all calculator buttons.
buttons_frame = Frame(main_frame)
buttons_frame.pack(fill="both", expand=True)

# Button layout.
buttons = [
    ["CE", "C", "⌫", "÷"],
    ["7", "8", "9", "×"],
    ["4", "5", "6", "−"],
    ["1", "2", "3", "+"],
    ["±", "0", ".", "="],
]

# Give all columns and rows equal weight.
for i in range(4):
    buttons_frame.columnconfigure(i, weight=1, uniform="buttons")

for i in range(5):
    buttons_frame.rowconfigure(i, weight=1, uniform="buttons")

# Create and position the buttons.
for row_index, row in enumerate(buttons):
    for column_index, text in enumerate(row):
        button = Button(
            buttons_frame,
            text=text,
            font=("Arial", 18),
            bd=1,
            relief="solid",
            command=lambda value=text: handle_display(value),
        )
        button.grid(
            row=row_index,
            column=column_index,
            sticky="nsew",
            padx=0,
            pady=0,
        )

# Start the Tkinter event loop.
window.mainloop()
