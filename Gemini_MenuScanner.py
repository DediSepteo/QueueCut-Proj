import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import google.generativeai as genai
import pandas as pd
import os

# Read the API key from the file
try:
    with open("apikey.txt", "r") as file:
        GOOGLE_API_KEY = file.read().strip()
except FileNotFoundError:
    messagebox.showerror("Error", "API key file not found.")
    exit(1)
except Exception as e:
    messagebox.showerror("Error", f"An error occurred while reading the API key: {e}")
    exit(1)

genai.configure(api_key="GOOGLE_API_KEY")

# this is where u put your model in
model = genai.GenerativeModel(model_name="gemini-1.5-flash") #choose the type of gemini model you want use 

uploaded_image_path = None
menu_data = []

def clean_response_text(response_text):
    """Remove the first '|' from each line in the response text."""
    lines = response_text.split('\n')
    cleaned_lines = [line[1:].strip() if line.startswith('|') else line for line in lines]
    return '\n'.join(cleaned_lines)

def process_input():
    user_input = input_entry.get().strip()
    if user_input == "":
        result_text.insert(tk.END, "Please enter a question.\n")
        return

    try:
        if uploaded_image_path:
            img = Image.open(uploaded_image_path)
            response = model.generate_content([user_input, img])
        else:
            response = model.generate_content(user_input)
        
        response_text = response.text
        # Clean the response text to remove the first '|'
        cleaned_response_text = clean_response_text(response_text)
        result_text.insert(tk.END, f"\n{cleaned_response_text}\n")
        parsed_items = parse_response(cleaned_response_text)
        menu_data.extend(parsed_items)

    except Exception as e:
        result_text.insert(tk.END, f"Error: {e}\n")

def parse_response(response_text):
    items = []
    lines = response_text.strip().split('\n')
    for line in lines[2:]:
        parts = [part.strip() for part in line.split('|')]
        if len(parts) >= 5:
            item = {
                "Category": parts[0] if parts[0] else "Unknown",
                "Item": parts[1] if parts[1] else "Unknown",
                "Price": parts[2] if parts[2] else "Unknown",
                "Description": parts[3] if parts[3] else "No Description",
                "Add ons": parts[4] if len(parts) > 4 else "None"
            }
            items.append(item)
    return items

def upload_image():
    global uploaded_image_path
    file_path = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
    )
    if not file_path:
        return

    try:
        image = Image.open(file_path)
        image.thumbnail((400, 400))
        img = ImageTk.PhotoImage(image)
        img_label.config(image=img)
        img_label.image = img
        img_path_label.config(text=f"Selected Image: {os.path.basename(file_path)}")
        uploaded_image_path = file_path
    except Exception as e:
        messagebox.showerror("Error", f"Unable to open image file: {e}")
        uploaded_image_path = None

def save_to_excel():
    if menu_data:
        df = pd.DataFrame(menu_data)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if save_path:
            df.to_excel(save_path, index=False, engine='openpyxl')
            messagebox.showinfo("Success", f"Menu saved to {save_path}")
    else:
        messagebox.showinfo("Info", "No menu data to save.")

def clear_output():
    """Clear the result_text and reset relevant variables."""
    result_text.delete(1.0, tk.END)
    img_label.config(image='')  # Clear the image
    img_path_label.config(text='')
    input_entry.delete(0, tk.END)
    global menu_data
    menu_data = []
    global uploaded_image_path
    uploaded_image_path = None

root = tk.Tk()
root.title("Generative AI Menu Creator")

input_label = tk.Label(root, text="Ask a question:")
input_label.pack(pady=10)

input_entry = tk.Entry(root, width=40)
input_entry.pack(pady=10)

submit_button = tk.Button(root, text="Submit", command=process_input)
submit_button.pack(pady=10)

upload_button = tk.Button(root, text="Upload Image", command=upload_image)
upload_button.pack(pady=10)

save_button = tk.Button(root, text="Save to Excel", command=save_to_excel)
save_button.pack(pady=10)

clear_button = tk.Button(root, text="Clear", command=clear_output)
clear_button.pack(pady=10)

img_label = tk.Label(root)
img_label.pack(pady=10)

img_path_label = tk.Label(root, text="")
img_path_label.pack(pady=5)

result_frame = tk.Frame(root)
result_frame.pack(pady=5)

result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, width=70, height=20)
result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

root.mainloop()
