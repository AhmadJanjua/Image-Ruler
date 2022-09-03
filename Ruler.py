import pyautogui as pg
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from types import NoneType
from PIL import Image, ImageTk
from pillow_heif import register_heif_opener
from math import sqrt

# Plugin to support heif or heic files; common for smartphones.
register_heif_opener()

# Get screen dimensions
WIDTH, HEIGHT = pg.size()

# Supported File types
FILE_TYPES = [
    (('JPEG Files'), ('*.jpg', '*.jpeg')),
    (('PNG Files'), ('*.png')),
    (('HEIF Files'), ('*.HEIF', '*.heic'))
]

class Ruler:

    # Constructor
    def __init__(self):

        # Coordinate for refrence object and actual object to be determined;
        self.ref_pt1 = [-1,-1]
        self.ref_pt2 = [-1,-1]
        self.act_pt1 = [-1,-1]
        self.act_pt2 = [-1,-1]

        # Refrence object size
        self.ref_len = -1

        # Setup Main window
        self.root = tk.Tk()
        self.root.title("Digital Ruler")
        self.root.config(background="Grey")

        # Need a refrence to this widget
        self.my_image = tk.Label(self.root)

    # Main Program
    def main(self):

        # Get file or close the program
        my_file = filedialog.askopenfilename(initialdir='.', filetypes=FILE_TYPES)
        if(my_file == ''):
            self.root.destroy()
            exit(0)
        
        # Open the file
        img = Image.open(my_file)

        # Resize Image
        width, height = img.size[0], img.size[1]
        scale = Ruler.get_scale(width, height) * 0.9
        width, height = int(img.size[0]*scale), int(img.size[1]*scale)
        img = img.resize((width,height), Image.Resampling.LANCZOS)

        # Display image in root panel
        imgtk = ImageTk.PhotoImage(img)
        self.my_image.config(image=imgtk)
        self.my_image.image = imgtk
        self.my_image.grid(column=0,row=0, rowspan=50)

        #Create All Labels

        # Coordinate labels and buttons
        Ruler.create_Label(self, "Refrence", self.ref_pt1, self.ref_pt2, 1)
        Ruler.create_Label(self, "Actual", self.act_pt1, self.act_pt2, 4)
        # Setting refrence length labels and button
        tk.Label(self.root, text="Refrence Object Length:", bg="Grey").grid(column=1,columnspan=2,row=6)
        tk.Label(self.root, text='Refrence Length: {x}'.format(x=self.ref_len)).grid(column=1,row=7, columnspan=2)
        tk.Button(self.root, text="Set Refrence Length", fg= "blue", command= lambda: Ruler.set_ref(self)).grid(column=1,row=8, columnspan=2)
        # Submit label and button
        tk.Label(self.root, text="Actual Object Length:", bg="Grey").grid(column=1,columnspan=2,row=9)
        tk.Label(self.root, text='...').grid(column=1,row=10, columnspan=2)
        tk.Button(self.root, text='Submit', fg= "blue", command=lambda: Ruler.submit(self)).grid(column=1,row=11, columnspan=2)

        # Usage instructions
        messagebox.showinfo("Instructions",
            "Select the refrence object using left click on the mouse.\n"+
            "Select the actual object using right click.")
        
        # Bind left and right mousepress to action
        # Left
        self.root.bind('<1>', lambda event: Ruler.click(self,event,self.ref_pt1, self.ref_pt2, 1))
        # Right
        self.root.bind('<3>', lambda event: Ruler.click(self,event,self.act_pt1, self.act_pt2, 4))

        self.root.mainloop()

    # Size the given image to best fit the window
    def get_scale(width, height):
        w_percent = ((WIDTH-400)/float(width))
        h_percent = (HEIGHT/float(height))
        if(w_percent < h_percent):
            return w_percent
        else:
            return h_percent

    # Create labels and buttons for coordinate tracking
    def create_Label(self, name, pt1, pt2, row):
        text1 = name + " Object Coordinates:"
        text2 = "Reset " + name + " Coordinates"
        tk.Label(self.root, text=text1, bg="Grey").grid(column=1,columnspan=2,row=row-1)
        tk.Label(self.root, text='Start: ({x},{y})'.format(x=pt1[0],y=pt1[1])).grid(column=1,row=row)
        tk.Label(self.root, text='End: ({x},{y})'.format(x=pt2[0],y=pt2[1])).grid(column=2,row=row)
        tk.Button(self.root, text=text2, fg="blue", command= lambda:  Ruler.reset(self,pt1,pt2,row)).grid(column=1, columnspan=2, row=row+1)

    # Calculate distance given two points
    def distance(pt1,pt2):
        square_sum = ( (pt1[0]-pt2[0]) ** 2 ) + ( (pt1[1]-pt2[1]) ** 2 )
        return sqrt( square_sum )

    # Register the coordinate of the pixel on the picture pressed
    def click(self, event, pt1, pt2, row):
        # Check if the press is not the image
        if(event.widget != self.my_image):
            return
        #register the first point then the second
        if (pt1[0] < 0):
            pt1[0],pt1[1] = event.x, event.y
            self.root.grid_slaves(column= 1, row=row)[0].destroy()
            tk.Label(self.root, text='Start: ({x},{y})'.format(x=pt1[0],y=pt1[1])).grid(column=1,row=row)
        elif(pt2[0] < 0):
            pt2[0], pt2[1] = event.x, event.y
            self.root.grid_slaves(column= 2, row=row)[0].destroy()
            tk.Label(self.root, text='End: ({x},{y})'.format(x=pt2[0],y=pt2[1])).grid(column=2,row=row)
    
    # Reset the coordinates for the given button
    def reset(self, pt1, pt2, row):
        pt1[0] = pt1[1] = pt2[0] = pt2[1] = -1
        self.root.grid_slaves(column= 1, row=row)[0].destroy()
        self.root.grid_slaves(column= 2, row=row)[0].destroy()
        tk.Label(self.root, text='Start: (-1,-1)').grid(column=1,row=row)
        tk.Label(self.root, text='End: (-1,-1)').grid(column=2,row=row)

    # Opens up a dialogue box that requests a float, then sets that as the refrence objects length
    def set_ref(self):
        value = simpledialog.askfloat("Input", "Please enter the length of the refrence object", minvalue=0)
        if value is NoneType:
            messagebox.showerror("No input","Please enter an input!")
        elif(value == 0):
            messagebox.showerror("Length Error","Please try again with larger value!")
        else:
            self.root.grid_slaves(column=1, row=7)[0].destroy()
            self.ref_len = value
            tk.Label(self.root, text='Refrence Length: {x}'.format(x=self.ref_len)).grid(column=1,row=7, columnspan=2)

    # Verify that the input fields and calculate the actual size
    def submit(self):
        # Check for missed inputs
        if(self.ref_len <=0):
            messagebox.showerror("Error","Please Change Refrence length!")
            return
        if(self.ref_pt1[0] < 0 or self.ref_pt2[0] < 0 or self.ref_pt1 == self.ref_pt2):
            messagebox.showerror("Error","Please Change Refrence Object Coordinates!")
            return
        if(self.act_pt1[0] < 0 or self.act_pt2[0] < 0 or self.act_pt1 == self.act_pt2):
            messagebox.showerror("Error","Please Change Actual Object Coordinates!")
            return 
        
        # Calculate distances and calculate actual size
        dist1 = Ruler.distance(self.ref_pt1, self.ref_pt2)
        dist2 = Ruler.distance(self.act_pt1, self.act_pt2)
        actual = dist2 * (self.ref_len/dist1)

        # Display the results
        self.root.grid_slaves(column=1, row=10)[0].destroy()
        tk.Label(self.root, text=actual).grid(column=1,row=10, columnspan=2)

# Start the program
if __name__ == "__main__":
    start = Ruler()
    start.main()