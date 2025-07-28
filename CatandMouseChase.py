import tkinter as tk
import random
import math

def create_chase_animation():
    """
    Creates a Tkinter window with a canvas and animates a CAT chasing a Mouse.
    The 'chased' Mouse moves randomly, and the 'chasing' CAT moves towards it.
    The animation stops when the chasing CAT "catches" the chased Mouse.
    """
    # --- Setup the main window ---
    root = tk.Tk()
    root.title("Mouse and CAT Chase") # Updated title
    root.geometry("800x600") # Larger window for the chase scene
    root.resizable(False, False) # Prevent resizing for simpler coordinate management

    # --- Create the canvas ---
    # Use fixed dimensions for canvas, which are then used for calculations
    CANVAS_WIDTH = 780 
    CANVAS_HEIGHT = 580
    canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="#E0FFFF", bd=2, relief="groove") # Light cyan background for a techy feel
    canvas.pack(pady=10)

    # --- Object Properties ---
    # Chased Mouse properties (formerly CAT)
    chased_object_width = 60 # Swapped width
    chased_object_height = 60 # Swapped height
    chased_object_color = "red" # Swapped color
    chased_object_speed = 10 # Swapped speed

    # Chasing CAT properties (formerly Mouse)
    chasing_object_width = 100 # Swapped width
    chasing_object_height = 100 # Swapped height
    chasing_object_color = "blue" # Swapped color
    chasing_object_speed = 20 # Swapped speed

    # --- Initial Positions ---
    # Place chased Mouse randomly in the middle-left part of the canvas (formerly CAT's initial position)
    initial_chased_object_x = random.randint(20, CANVAS_WIDTH // 2 - chased_object_width - 20)
    initial_chased_object_y = random.randint(20, CANVAS_HEIGHT - chased_object_height - 20)

    # Place chasing CAT randomly in the middle-right part of the canvas (formerly Mouse's initial position)
    initial_chasing_object_x = random.randint(CANVAS_WIDTH // 2, CANVAS_WIDTH - chasing_object_width - 20)
    initial_chasing_object_y = random.randint(20, CANVAS_HEIGHT - chasing_object_height - 20)

    # --- Create Canvas Objects ---
    # Chased Mouse
    chased_object_id = canvas.create_rectangle(
        initial_chased_object_x, initial_chased_object_y,
        initial_chased_object_x + chased_object_width, initial_chased_object_y + chased_object_height,
        fill=chased_object_color, outline="darkred", width=2, tags="chased_object" # Swapped outline
    )
    chased_object_text_id = canvas.create_text(
        initial_chased_object_x + chased_object_width / 2, initial_chased_object_y + chased_object_height / 2,
        text="Mouse", fill="white", font=("Arial", 10, "bold"), tags="chased_object_text" # Changed to Mouse
    )

    # Chasing CAT
    chasing_object_id = canvas.create_rectangle(
        initial_chasing_object_x, initial_chasing_object_y,
        initial_chasing_object_x + chasing_object_width, initial_chasing_object_y + chasing_object_height,
        fill=chasing_object_color, outline="darkblue", width=2, tags="chasing_object" # Swapped outline
    )
    chasing_object_text_id = canvas.create_text(
        initial_chasing_object_x + chasing_object_width / 2, initial_chasing_object_y + chasing_object_height / 2,
        text="CAT", fill="white", font=("Arial", 10, "bold"), tags="chasing_object_text" # Changed to CAT
    )

    # --- Game State Variables ---
    game_over = False
    animation_delay = 50 # Milliseconds between frames (20 FPS)

    # --- Helper Function to get object center coordinates ---
    def get_center(obj_id):
        coords = canvas.coords(obj_id)
        if not coords: return 0, 0 # Handle case where object might be deleted
        x1, y1, x2, y2 = coords
        return (x1 + x2) / 2, (y1 + y2) / 2

    # --- Animation Function ---
    def animate_chase():
        nonlocal game_over

        if game_over:
            return # Stop the animation

        # Get current positions
        chased_object_coords = canvas.coords(chased_object_id)
        chasing_object_coords = canvas.coords(chasing_object_id)

        if not chased_object_coords or not chasing_object_coords: # Check if objects still exist
            return

        e_x1, e_y1, e_x2, e_y2 = chased_object_coords
        d_x1, d_y1, d_x2, d_y2 = chasing_object_coords

        # --- Chased Mouse Random Movement ---
        # Generate small random movement for chased Mouse
        e_dx = random.uniform(-chased_object_speed, chased_object_speed)
        e_dy = random.uniform(-chased_object_speed, chased_object_speed)

        # Calculate next chased Mouse position
        next_e_x1, next_e_y1 = e_x1 + e_dx, e_y1 + e_dy
        next_e_x2, next_e_y2 = e_x2 + e_dx, e_y2 + e_dy

        # Keep chased Mouse within canvas boundaries
        if next_e_x1 < 0: e_dx = abs(e_dx)
        if next_e_x2 > CANVAS_WIDTH: e_dx = -abs(e_dx)
        if next_e_y1 < 0: e_dy = abs(e_dy)
        if next_e_y2 > CANVAS_HEIGHT: e_dy = -abs(e_dy)

        canvas.move(chased_object_id, e_dx, e_dy)
        canvas.move(chased_object_text_id, e_dx, e_dy)

        # --- Chasing CAT Logic ---
        d_center_x, d_center_y = get_center(chasing_object_id)
        e_center_x, e_center_y = get_center(chased_object_id)

        # Calculate direction vector from chasing CAT to chased Mouse
        dir_x = e_center_x - d_center_x
        dir_y = e_center_y - d_center_y

        # Calculate distance
        distance = math.sqrt(dir_x**2 + dir_y**2)

        # Move chasing CAT towards chased Mouse if not too close
        if distance > chasing_object_speed: # Move only if not already on top of chased object
            # Normalize direction vector and multiply by chasing CAT speed
            move_x = (dir_x / distance) * chasing_object_speed
            move_y = (dir_y / distance) * chasing_object_speed
        else:
            move_x, move_y = 0, 0 # Stop moving if very close, collision will handle it

        # Calculate next chasing CAT position
        next_d_x1, next_d_y1 = d_x1 + move_x, d_y1 + move_y
        next_d_x2, next_d_y2 = d_x2 + move_x, d_y2 + move_y

        # Keep chasing CAT within canvas boundaries (simple bounce if hits edge)
        if next_d_x1 < 0 or next_d_x2 > CANVAS_WIDTH:
            move_x = -move_x # Just reverse if it hits the edge
        if next_d_y1 < 0 or next_d_y2 > CANVAS_HEIGHT:
            move_y = -move_y # Just reverse if it hits the edge

        canvas.move(chasing_object_id, move_x, move_y)
        canvas.move(chasing_object_text_id, move_x, move_y)

        # --- Collision Detection (Chasing CAT catches Chased Mouse) ---
        # AABB collision check
        if (d_x1 < e_x2 and d_x2 > e_x1 and
            d_y1 < e_y2 and d_y2 > e_y1):
            game_over = True
            canvas.create_text(
                CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2, # Use fixed dimensions for text centering
                text="GAME OVER!\nCAT Caught Mouse!", # Updated game over message
                fill="red", font=("Arial", 24, "bold"), tags="game_over_text"
            )
            return # Stop further animation steps

        # Schedule the next animation step
        root.after(animation_delay, animate_chase)

    # Start the animation loop
    animate_chase()

    # Run the Tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    create_chase_animation()