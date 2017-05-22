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

name = "DEFAULT"

def first_pass(commands ):
    global name
    b = False
    f = False
    v = False 
    num_frames = 1
    for c in commands:
        if c[0] == 'basename':
            name = c[1]
            b = True
        elif c[0] == 'frames':
            num_frames = c[1]
            f = True
        elif c[0] == 'vary':
            v = True
    if (not f) and v:
        print "NO FRAMES.. EXITING"
        sys.exit()
    if (not b) and f:
        print "USING \"DEFAULT\" as basename, because no other name specified"
    return num_frames


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
    for i in range(num_frames):
        knobs.append({})

    for c in commands:
        if c[0] == "vary":
            
            if c[4] < 0 or c[5] > num_frames:
                print "ERROR: IMPOSSIBLE VARY RANGE"
                sys.exit()

            i = 1.0*(c[5] - c[4])/(c[3] - c[2] + 1)
            j = c[4]
            for i in range(c[2], c[3] + 1):
                knobs[i][c[1]] = j
                j += i
    return knobs

def run(filename):
    """
    This function runs an mdl script
    """
    color = [255, 255, 255]

    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return  
    
    num_frames = first_pass(commands)
    if num_frames > 1:
        knobs = second_pass(commands, num_frames)



    for frame in xrange(num_frames):
        tmp = new_matrix()
        ident(tmp)
        stack = [ [x[:] for x in tmp] ]
        tmp = []
        screen = new_screen()
        step = 0.1
        knob = 1
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
                if num_frames > 1 and args[3] != None:
                    foo = args[3]
                    knob = knobs[frame][foo]

                tmp = make_translate(args[0]*knob, args[1]*knob, args[2]*knob)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                if num_frames > 1 and args[3] != None:
                    foo = args[3]
                    knob = knobs[frame][foo]
                
                tmp = make_scale(args[0]*knob, args[1]*knob, args[2]*knob)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                if num_frames > 1 and args[2] != None:
                    foo = args[2]
                    knob = knobs[frame][foo]
                
                theta = args[1] * (math.pi/180) * knob
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
                save_extension(screen, "anim/" + name + "%03d.png"%frame)

