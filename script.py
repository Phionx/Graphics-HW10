import mdl
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands, symbols ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)
  
  Should set num_frames and basename if the frames 
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.

  jdyrlandweaver
  ==================== """

def first_pass(commands ):
    basename = "DEFAULT"
    num_frames = 0
    for c in commands:
        if c[0] == 'basename':
            basename = c[1]
        elif c[0] == 'frames':
            if len([x for x in commands if x[0] == 'basename'])== 0:
                print "Name is \"DEFAULT\""
            num_frames = int(c[1])
        elif c[0] == 'vary':
            if len([x for x in commands if x[0] == 'frames']) == 0:
                print "No frames while using 'vary' >> Exiting."
                return (True, basename, num_frames)
    return (False, basename, num_frames)


"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go 
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value. 
  ===================="""
def second_pass( commands, num_frames ):
    knobs = []
    i = 0
    while i < num_frames:
        knobs.append({})
        i+=1

    i = 0
    for c in commands[0]:
        if c[0] == "vary":
            for i in range (int(c[2]), int(c[3])+1):
                if float(c[5]) > float(c[4]):
                    knobs[i][c[1]] = float(c[5]-c[4])/(int(c[3])-int(c[2])+1)*(i-int(c[2]) +1)
                else:
                    knobs[i][c[1]] = float(c[4]) - float(c[4]-c[5])/(int(c[3]) - int(c[2]) + 1)*(i - int(c[2]) + 1)
    return knobs

def run(filename):
    """
    This function runs an mdl script
    """
    basename = -1
    num_frames = -1
    color = [255, 255, 255]
    tmp = new_matrix()
    ident( tmp )

    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return  
    if first_pass(commands)[0]:
        return
    basename = first_pass(commands)[1]
    num_frames = first_pass(commands)[2]
    if not num_frames > 1:
        num_frames = 1
    second = second_pass(p, num_frames)

    ident(tmp)
    stack = [ [x[:] for x in tmp] ]
    screen = new_screen()
    tmp = []
    step = 0.1
    for frame in xrange(num_frames):
        for command in commands:
            print command
            c = command[0]
            args = command[1:]

            if c == 'box':
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'sphere':
                add_sphere(tmp,
                         args[0], args[1], args[2], args[3], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'torus':
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'move':
                tmp = make_translate(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                tmp = make_scale(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                theta = args[1] * (math.pi/180)
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
        if num_frames > 1:
            save_extension(screen, "anim/" + basename + "%03d.png"%frame)
            clear_screen(screen)
            stack.pop()
    if num_frames > 1:
        make_animation(basename)
