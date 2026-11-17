from tkinter import *
import math

# TODO: Improve percentage calculations.
# TODO: Add keyboard shortcuts.
# TODO: Add calculation history.


def clear_display():
    # Clear the entire display.
    display.delete(0, END)
    update_display_font()


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
        return f"{number:.7g}"

    return normal_result


def is_operator(value):
    # Check whether the character is an operator.
    return value in ("+", "−", "×", "÷")


def get_last_number(expression):
    # Find the position of the last operator.
    last_operator = max(
        expression.rfind("+"),
        expression.rfind("−"),
        expression.rfind("×"),
        expression.rfind("÷"),
    )

    # Return the last number in the expression.
    return expression[last_operator + 1 :]


def update_display_font():
    length = len(display.get())

    if length <= 11:
        size = display_font_size
    else:
        size = round(
            display_font_size - (length - 11) * (display_font_size - min_font_size) / 5
        )

    size = max(min_font_size, size)
    display.config(font=("Arial", size))


def can_insert_decimal():
    current = display.get()
    last_number = get_last_number(current)

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

    current = display.get()

    # Limit each number to 16 characters.
    if value in "0123456789.":
        last_number = get_last_number(current)

        if len(last_number) >= 16:
            return

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
        update_display_font()

    # Calculate the expression.
    elif value == "=":
        calculate()

    # Change the sign of the last number.
    elif value == "±":
        toggle_sign()
        update_display_font()

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
                update_display_font()
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
        update_display_font()


def toggle_sign():
    global result_shown

    current = display.get()

    # Return if the display is empty or ends with an operator.
    if not current or is_operator(current[-1]):
        return

    last_number = get_last_number(current)

    # Return if the last number is zero or invalid.
    try:
        if float(last_number) == 0:
            return
    except ValueError:
        return

    # Change the sign of the entire result.
    if result_shown:
        number = float(current)
        clear_display()
        display.insert(END, format_result(-number))
        return

    # Find the beginning of the last number.
    start = len(current) - len(last_number)

    # Remove the negative sign or insert one.
    if current[start] == "-":
        display.delete(start, start + 1)
    else:
        display.insert(start, "-")


def apply_unary_operation(operation):
    global result_shown

    current = display.get()

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
        update_display_font()

    except (ValueError, ZeroDivisionError, OverflowError):
        # Display an error if the operation is invalid.
        clear_display()
        display.insert(END, "ERROR")
        result_shown = True
        update_display_font()


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
        update_display_font()

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
        update_display_font()


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
        # Keep the original number if no calculation is performed.
        if expression.lstrip("-").replace(".", "", 1).isdigit():
            result = expression
        else:
            result = format_result(eval(expression))

        clear_display()
        display.insert(END, result)
        result_shown = True
        update_display_font()

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
        update_display_font()


# Create the main window.
window = Tk()
window.title("Calculator")
window.geometry("320x500")
window.minsize(height=280, width=180)

result_shown = False

# Create the main frame.
main_frame = Frame(window, padx=3, pady=3)
main_frame.pack(fill="both", expand=True)

# Create the calculator display.
display_frame = Frame(main_frame, height=120)
display_frame.pack(fill="x")
display_frame.pack_propagate(False)

display_font_size = 36
min_font_size = 24

display = Entry(
    display_frame,
    font=("Arial", display_font_size),
    justify="right",
)
display.pack(fill="both", expand=True)

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
