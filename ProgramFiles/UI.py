# UI.py

import tkinter as tk
from tkinter import filedialog
import customtkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from logic import App
import sys
from io import StringIO
import serial.tools.list_ports
import time
import threading
import os
from datetime import datetime
import csv
import traceback
import pandas as pd

class UIApp:
    def __init__(self, root):
        # Ensure x and y are sequences when calling animation

        self.position = []
        self.magneticFieldMagnitude = []
        self.magneticFieldX = []
        self.magneticFieldY = []
        self.magneticFieldZ = []

        self.logic_app = App(root)
        self.root = root
        #self.animation(x=[0], y=[0])
        self.root.title("Magnetic Field Plotter")
        self.default_font = ("Arial", 12)
        self.root.option_add("*Font", self.default_font)

        # Configure the root window to expand
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.create_menu_bar()
        self.create_widgets()
        self.init_plot()
        
        # Start the serial connection in a separate thread
        self.serial_thread = threading.Thread(target=self.startSerial)
        self.serial_thread.start()

    def startSerial(self):
        try:
            while True:
                while True:          
                    # Create gaussmeter connection
                    ports = serial.tools.list_ports.comports()
                    active_ports = [port.device for port in ports]
                    
                    for port in active_ports:
                        #print(f'Trying port: {port}')
                        self.logic_app.serial_connect_gaussmeter(port)

                    if self.logic_app.has_serial_connect()[0] == True:
                        print(f"Gaussmeter connected: {self.logic_app.has_serial_connect()[0]}\n\n")
                        break
                    else:
                        print('Gaussmeter cannot connect.\nRetrying connection in 5 seconds...\n')
                        time.sleep(5)

                while self.logic_app.has_serial_connect()[1] == False:
                    ports = serial.tools.list_ports.comports()
                    active_ports = [port.device for port in ports]

                    for port in active_ports:
                        self.logic_app.serial_connect_motor(port)

                    if self.logic_app.has_serial_connect()[1] == True:
                        print(f"Motors connected: {self.logic_app.has_serial_connect()[1]}\n\n")
                        break
                    else:
                        print('Motors cannot connect.\nRetrying connection in 5 seconds...\n')
                        time.sleep(5) 
                break 
        except Exception as e:
            traceback.print_exc()


    def create_menu_bar(self):
        try:
            menu_bar = tk.Menu(self.root, bg="black")
            self.root.config(menu=menu_bar)
            
            # File Menu
            file_menu = tk.Menu(menu_bar, tearoff=0)
            file_menu.add_command(label="Exit", command=self.exitCommand, font=('Courier', 10))
            menu_bar.add_cascade(label="File", menu=file_menu, font=('Courier', 10))
            file_menu.add_command(label="Save Field", command=self.save_field_result, font=('Courier', 10))
            
            # Options Menu
            options_menu = tk.Menu(menu_bar, tearoff=0)
            options_menu.add_command(label="Info", command=self.open_info_popup, font=('Courier', 10))
            menu_bar.add_cascade(label="Options", menu=options_menu)
        except Exception as e:
            traceback.print_exc()

    def exitCommand(self):
        self.logic_app.closeCOMports()
        self.root.destroy()  # Close the Tkinter application window

    def save_field_result(self):
        data = {
            'Position': self.position,
            'Bx': self.magneticFieldX,
            'By': self.magneticFieldY,
            'Bz': self.magneticFieldZ,
            'MagneticFieldMagnitude': self.magneticFieldMagnitude
        }
        df = pd.DataFrame(data)

        # Create the root window
        root = tk.Tk()
        root.withdraw()  # Hide the root window

        # Open a file dialog to choose where to save the CSV
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save CSV File",
            initialfile=f'MagneticFieldPlot, {datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
        )

        if file_path:
            # Save the data to the chosen file path
            df.to_csv(file_path, index=False)
            print(f"CSV file saved to {file_path}")

    def open_info_popup(self):
        # Create a new window for the info popup
        info_window = customtkinter.CTkToplevel(self.root)
        info_window.title("Info")
        
        # Set the background color to dark
        info_window.configure(bg='black')
        
        # Read the text from the file
        file_path = os.path.join("fieldplotter", "info.txt")
        if not os.path.isfile(file_path):
            text = "No info file found."
        else:
            with open(file_path, "r") as file:
                text = file.read()
        
        # Create a text widget to display the file content
        text_widget = tk.Text(info_window, wrap=tk.WORD, bg='black', fg='lime', font=('Courier', 10))
        text_widget.insert(tk.END, text)
        text_widget.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Add a scrollbar to the text widget
        scrollbar = tk.Scrollbar(info_window, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)

    def list_active_com_ports(self):
        ports = serial.tools.list_ports.comports()
        active_ports = []
        for port in ports:
            active_ports.append(port.device)
        return active_ports


    def create_widgets(self):
        # Frame to hold the graph plot
        self.plot_frame = customtkinter.CTkFrame(self.root)
        self.plot_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Frame to hold input commands
        self.input_frame = customtkinter.CTkFrame(self.root)
        self.input_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Configure the root window to expand
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Configure frames to expand
        self.plot_frame.grid_rowconfigure(0, weight=1)
        self.plot_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_columnconfigure(1, weight=1)
        self.input_frame.grid_rowconfigure(6, weight=1)  # Ensure console output expands

        # Labels and entries for min, max, increment
        customtkinter.CTkLabel(self.input_frame, text="Axis").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.axis_entry = customtkinter.CTkComboBox(self.input_frame, values=["X", "Y", "Z"])
        self.axis_entry.grid(row=0, column=1, padx=5, pady=5)

        customtkinter.CTkLabel(self.input_frame, text="Min (cm):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.min_entry = customtkinter.CTkEntry(self.input_frame)
        self.min_entry.grid(row=1, column=1, padx=5, pady=5)
        
        customtkinter.CTkLabel(self.input_frame, text="Max (cm):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.max_entry = customtkinter.CTkEntry(self.input_frame)
        self.max_entry.grid(row=2, column=1, padx=5, pady=5)
        
        customtkinter.CTkLabel(self.input_frame, text="Increment (cm):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.inc_entry = customtkinter.CTkEntry(self.input_frame)
        self.inc_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Button to start plot
        self.plot_button = customtkinter.CTkButton(self.input_frame, text="Start", command=self.start_plot)
        self.plot_button.grid(row=4, column=0, columnspan=2, padx=5, pady=10)
        
        # Button to stop plot
        self.stop_button = customtkinter.CTkButton(self.input_frame, text="Stop", command=self.stop_plot)
        self.stop_button.grid(row=5, column=0, columnspan=2, padx=5, pady=10)
        
        # Text widget to display console output
        self.console_output = tk.Text(self.input_frame, height=10, width=30, wrap=tk.WORD, bg='black', fg='lime', font=('Courier', 10))
        self.console_output.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        # Redirect stdout to the Text widget
        self.redirect_stdout()




    def redirect_stdout(self):
        # Create a StringIO buffer
        self.output_buffer = StringIO()

        # Define a function to write to both the buffer and the Text widget
        def write(message):
            self.output_buffer.write(message)
            self.console_output.insert(tk.END, message)
            self.console_output.see(tk.END)  # Scroll to the end of the Text widget

        # Replace sys.stdout with our custom write function
        sys.stdout.write = write


    def init_plot(self):
        self.fig, self.ax = plt.subplots()

        # Customize the plot for a dark and modern look
        dark_color = '#2E2E2E'
        self.ax.set_facecolor(dark_color)  # Set the background color of the plot
        self.fig.patch.set_facecolor(dark_color)  # Set the background color of the figure

        self.line, = self.ax.plot([], [], linewidth=2, linestyle='-', color='cyan')
        self.ax.set_xlabel('Distance (cm)', color='white')
        self.ax.set_ylabel('Magnetic Field (G)', color='white')

        # Customize axis colors and styles
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color('white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.ax.yaxis.label.set_color('white')
        self.ax.xaxis.label.set_color('white')
        self.ax.title.set_color('white')

        # Embed the plot in the customtkinter frame using FigureCanvasTkAgg
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        self.animation(x=[0], y=[0])

    def animation(self, x, y):
        self.line.set_data(x, y)
        self.ax.relim()
        self.ax.autoscale_view(True,True,True)
        self.canvas.draw()
        self.canvas.flush_events()
        
    def update_plot(self):
        pass
    
    def stop_plot(self):
        print('Stopping...')
        didClose = self.logic_app.closeCOMports()
        if didClose == True:
            print('Closed serial ports sucessfully.')
        else :
            print('Error in closing serial ports.')

    def validInputParameters(self):
        try:
            startPos = float(self.min_entry.get())
            endPos = float(self.max_entry.get())
            increment = float(self.inc_entry.get())

            if startPos >= endPos or startPos == 0 or endPos == 0 or increment == 0 or increment >= abs(startPos - endPos):
                return False
            else:
                return True
        except Exception as e:
            traceback.print_exc()

    def start_plot(self):
        startPos = float(self.min_entry.get())
        endPos = float(self.max_entry.get())
        increment = float(self.inc_entry.get())
        axis = str(self.axis_entry.get())
        self.position = []
        self.magneticFieldMagnitude = []
        self.magneticFieldX = []
        self.magneticFieldY = []
        self.magneticFieldZ = []
        gaussConnect, motorConnect = self.logic_app.has_serial_connect()

        if gaussConnect and motorConnect:
            print(f'Parameters:{startPos},{endPos},{increment}')

            if not os.path.exists("Results"):
                os.makedirs("Results")
            results_dir = f'FieldPlot_Axis={axis}_Min={startPos}_Max={endPos}_Increment={increment}_Time={datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
            filepath = os.path.join("Results", results_dir)

            with open(filepath, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Position', 'Bx', 'By','Bz', 'MagneticFieldMagnitude'])
                counter = 0
                steps = int((endPos-startPos)/increment)
                startTime = time.time()
                for step in np.arange(startPos, endPos, increment):
                    counter += 1
                    while self.logic_app.isMotorMoving() == True:
                        time.sleep(0.1)
                    self.position.append(step)
                    samples = 5
                    # Variables to accumulate the sums
                    sum_magneticFieldMagnitude = 0
                    sum_magneticFieldX = 0
                    sum_magneticFieldY = 0
                    sum_magneticFieldZ = 0
                    
                    for _ in range(samples):
                        magneticField = self.logic_app.getMagneticField()
                        sum_magneticFieldMagnitude += magneticField[3]
                        sum_magneticFieldX += magneticField[0]
                        sum_magneticFieldY += magneticField[1]
                        sum_magneticFieldZ += magneticField[2]
                    
                    # Calculate averages
                    avg_magneticFieldMagnitude = sum_magneticFieldMagnitude / samples
                    avg_magneticFieldX = sum_magneticFieldX / samples
                    avg_magneticFieldY = sum_magneticFieldY / samples
                    avg_magneticFieldZ = sum_magneticFieldZ / samples
                    
                    self.magneticFieldMagnitude.append(avg_magneticFieldMagnitude)
                    self.magneticFieldX.append(avg_magneticFieldX)
                    self.magneticFieldY.append(avg_magneticFieldY)
                    self.magneticFieldZ.append(avg_magneticFieldZ)

                    self.logic_app.moveMotor(-increment, axis)
                    writer.writerow([self.position[-1], self.magneticFieldX[-1], self.magneticFieldY[-1], self.magneticFieldZ[-1], self.magneticFieldMagnitude[-1]])
                    percentageFinished = int(100*counter/steps)
                    elapsedTime = time.time() - startTime
                    timeperStep = elapsedTime/counter
                    remainingTime = round((timeperStep*(steps-counter))/60, 1)
                    print(f'Position: {round(step,1)}, Steps: {counter}/{steps} ({percentageFinished}%), Time Remaining: {remainingTime} min')
                    self.animation(self.position, self.magneticFieldMagnitude)
            self.logic_app.endPlot()
            print('Field measurement complete.')
        else:
            self.startSerial()
        
def main():
  customtkinter.set_appearance_mode("dark")
  root = customtkinter.CTk()
  root.geometry("1200x700")  # width x height
  app = UIApp(root)
  root.mainloop()
    
if __name__ == "__main__":
  main()
