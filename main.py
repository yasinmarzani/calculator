from tkinter import *
import math
from decimal import Decimal


def clear_display():
    # Clear the entire display.
    display.delete(0, END)


def format_result(number):
    # Handle infinite and undefined results.
    if isinstance(number, float) and not math.isfinite(number):
        return str(number)

    # Convert the result to a string.
    normal_result = str(number)

    # Remove unnecessary decimal zeros from integer results.
    if isinstance(number, float) and number.is_integer():
        normal_result = str(int(number))

    # Use scientific notation for long results.
    if len(normal_result) > 12:
        if isinstance(number, int):
            return f"{Decimal(number):.6e}"

        return f"{number:.6e}"

    return normal_result


def is_operator(value):
    # Check whether the character is an operator.
    return value in ("+", "−", "×", "÷")


def can_insert_decimal():
    current = display.get()

    # Extract the last number from the expression.
    last_number = current

    for operator in ("+", "−", "×", "÷"):
        last_number = last_number.replace(operator, " ")

    last_number = last_number.split()[-1] if last_number.split() else ""

    # Check whether the last number already contains a decimal point.
    return "." not in last_number


def handle_display(value):
    global result_shown

    current = display.get()

    # Handle input after an error.
    if result_shown and current == "ERROR":
        if value in "0123456789.":
            clear_display()
            result_shown = False
        elif value in ("C", "CE", "⌫"):
            clear_display()
            result_shown = False
            return
        else:
            return

    # Start a new expression when a digit or decimal point is entered after a result.
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

    # Remove the last character from the display.
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

    # Apply unary operations.
    elif value in ("√", "x²", "1/x"):
        apply_unary_operation(value)

    # Calculate the percentage.
    elif value == "%":
        calculate_percentage()

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
    global result_shown

    current = display.get()

    # Return if the display is empty, zero, or ends with an operator.
    if not current or current == "0" or is_operator(current[-1]):
        return

    # Change the sign of the entire result.
    if result_shown:
        number = float(current)
        clear_display()
        display.insert(END, format_result(-number))
        return

    # Find the position of the last operator.
    last_operator = max(
        current.rfind("+"),
        current.rfind("−"),
        current.rfind("×"),
        current.rfind("÷"),
    )

    # Find the beginning of the last number.
    start = last_operator + 1

    # Remove the negative sign or insert one.
    if start < len(current) and current[start] == "-":
        display.delete(start, start + 1)
    else:
        display.insert(start, "-")


def apply_unary_operation(operation):
    global result_shown

    current = display.get()

    # Return if the display is empty.
    if not current:
        return

    try:
        number = float(current)

        # Apply the selected unary operation.
        if operation == "√":
            result = math.sqrt(number)
        elif operation == "x²":
            result = number**2
        elif operation == "1/x":
            result = 1 / number

        clear_display()
        display.insert(END, format_result(result))
        result_shown = True

    except (ValueError, ZeroDivisionError, OverflowError):
        # Display an error if the operation is invalid.
        clear_display()
        display.insert(END, "ERROR")
        result_shown = True


def calculate_percentage():
    global result_shown

    current = display.get()

    if not current:
        return

    # Remove the last operator before calculating the percentage.
    if is_operator(current[-1]):
        current = current[:-1]

    try:
        # Calculate the percentage of the displayed result.
        if result_shown:
            result = float(current) / 100

        else:
            # Find the position of the last operator.
            last_operator = max(
                current.rfind("+"),
                current.rfind("−"),
                current.rfind("×"),
                current.rfind("÷"),
            )

            if last_operator == -1:
                result = float(current) / 100

            else:
                first_number = float(current[:last_operator])
                second_number = float(current[last_operator + 1 :])

                operator = current[last_operator]

                # Calculate percentages differently for addition/subtraction and multiplication/division.
                if operator in ("+", "−"):
                    percentage = first_number * second_number / 100
                else:
                    percentage = second_number / 100

                expression = current[:last_operator] + operator + str(percentage)

                # Convert display operators into Python operators.
                expression = expression.replace("×", "*")
                expression = expression.replace("÷", "/")
                expression = expression.replace("−", "-")

                result = eval(expression)

        clear_display()
        display.insert(END, format_result(result))
        result_shown = True

    except (
        ValueError,
        SyntaxError,
        ZeroDivisionError,
        NameError,
        TypeError,
        OverflowError,
    ):
        # Display an error if the expression is invalid.
        clear_display()
        display.insert(END, "ERROR")
        result_shown = True


def calculate():
    global result_shown

    expression = display.get()

    # Ignore the last operator if the expression ends with one.
    if expression and is_operator(expression[-1]):
        expression = expression[:-1]

    # Convert display operators into Python operators.
    expression = expression.replace("×", "*")
    expression = expression.replace("÷", "/")
    expression = expression.replace("−", "-")

    try:
        # Evaluate the mathematical expression.
        result = eval(expression)

        clear_display()
        display.insert(END, format_result(result))
        result_shown = True

    except (
        SyntaxError,
        ZeroDivisionError,
        NameError,
        TypeError,
        OverflowError,
    ):
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

# Create the main frame.
main_frame = Frame(window, padx=3, pady=3)
main_frame.pack(fill="both", expand=True)

# Create the calculator display.
display = Entry(main_frame, font=("Arial", 36), justify="right")
display.pack(fill="x", ipady=28)

# Create the frame containing the calculator buttons.
buttons_frame = Frame(main_frame)
buttons_frame.pack(fill="both", expand=True)

# Define the button layout.
buttons = [
    ["%", "√", "x²", "1/x"],
    ["CE", "C", "⌫", "÷"],
    ["7", "8", "9", "×"],
    ["4", "5", "6", "−"],
    ["1", "2", "3", "+"],
    ["±", "0", ".", "="],
]

# Configure equal weights for all rows and columns.
for i in range(len(buttons[0])):
    buttons_frame.columnconfigure(i, weight=1, uniform="buttons")

for i in range(len(buttons)):
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
