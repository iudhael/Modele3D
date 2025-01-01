import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.images import *

import firebase_admin
from firebase_admin import credentials, db

gx = gy = gz = 0.0



# Chemin vers le fichier JSON téléchargé depuis Firebase
cred = credentials.Certificate('file.json')#/home/pi/file.json
# Initialiser l'application Firebase
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://url.firebaseio.com'
})

# Référence à la base de données
ref = db.reference('/')  # Remplace par le chemin approprié dans ta base de données


# Fonction pour charger le fichier .obj
def load_obj(filename):
    vertices = []
    textures = []
    normals = []
    faces = []
    
    with open(filename, 'r') as file:
        for line in file:
            if line.startswith('v '):  # Ligne contenant un sommet
                parts = line.split()
                vertex = [float(parts[1]), float(parts[2]), float(parts[3])]
                vertices.append(vertex)
            elif line.startswith('vt '):  # Ligne contenant une coordonnée de texture
                parts = line.split()
                texture = [float(parts[1]), float(parts[2])]
                textures.append(texture)
            elif line.startswith('vn '):  # Ligne contenant une normale
                parts = line.split()
                normal = [float(parts[1]), float(parts[2]), float(parts[3])]
                normals.append(normal)
            elif line.startswith('f '):  # Ligne contenant une face
                face = []
                texture_coords = []
                norms = []
                parts = line.split()[1:]
                
                for part in parts:
                    vals = part.split('/')
                    vertex_index = int(vals[0]) - 1
                    face.append(vertex_index)
                    
                    if len(vals) > 1 and vals[1]:  # Coordonnée de texture présente
                        texture_index = int(vals[1]) - 1
                        texture_coords.append(texture_index)
                    
                    if len(vals) > 2 and vals[2]:  # Normale présente
                        normal_index = int(vals[2]) - 1
                        norms.append(normal_index)
                
                faces.append((face, texture_coords, norms))
    
    return vertices, textures, normals, faces


# Fonction pour dessiner l'objet
def draw_obj(vertices, textures, normals, faces):
    
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -10)  # Recule la caméra
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    #draw()
    

    glRotatef(gz, 0.0, 1.0, 0.0)  # Yaw,   rotate around y-gxis
    glRotatef(gy ,1.0,0.0,0.0)        # Pitch, rotate around x-gxis
    glRotatef(-1*gx ,0.0,0.0,1.0)     # Roll,  rotate around z-gxis
    #glRotatef(gy, 0.0, 1.0, 0.0) 
    #glRotatef(gx ,1.0,0.0,0.0)   
    #glRotatef(gz ,0.0,0.0,1.0)   
    glBegin(GL_TRIANGLES)
    
    for face in faces:
        vertex_indices, texture_indices, normal_indices = face
        
        for i in range(len(vertex_indices)):
            if normal_indices:  # Si on a des normales, on les applique
                glNormal3fv(normals[normal_indices[i]])
            
            if texture_indices:  # Si on a des coordonnées de texture, on les applique
                glTexCoord2fv(textures[texture_indices[i]])
            
            glVertex3fv(vertices[vertex_indices[i]])
    glEnd()
    

def draw():
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    #glLoadIdentity()
    #glTranslatef(0,0.0,-7.0)
    glBegin(GL_LINES)
    
    glColor3f(0.0,1.0,0.0)
    glVertex3f( 0.0, 2.0,0.0)
    glVertex3f(0.0, -2.0,0.0)		
	

    glColor3f(1.0,0.0,0.0)		
    glVertex3f( 3.0, 0.0, 0.0)
    glVertex3f(-3.0, 0.0, 0.0)		

    glColor3f(0.0,0.0,1.0)	
    glVertex3f(0.2, 0.2, 2.0)
    glVertex3f(-0.2, -0.2, -2.0)		
	
    glEnd()	


         

def resize(width, height):
    if height==0:
        height=1
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.0*width/height, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def init():
    glShadeModel(GL_SMOOTH)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)


prev_gx = prev_gy = prev_gz = 0.0
def read_data():
    global gx, gy, gz
    global prev_gx, prev_gy, prev_gz
    
    data = ref.get()
    #print(data['data']['sensors']['gyroscope'])

    #gyro_x = data['data']['sensors']['accelerometer']['x']
    #gyro_y = data['data']['sensors']['accelerometer']['y']
    #gyro_z = data['data']['sensors']['accelerometer']['z']

    gyro_x = data['data']['sensors']['gyroscope']['x']
    gyro_y = data['data']['sensors']['gyroscope']['y']
    gyro_z = data['data']['sensors']['gyroscope']['z']


    if gyro_x != prev_gx or gyro_y != prev_gy or gyro_z != prev_gz:
        gx = gyro_x
        gy = gyro_y
        gz = gyro_z

        # Mettre à jour les anciennes valeurs
        prev_gx = gyro_x
        prev_gy = gyro_y
        prev_gz = gyro_z
    else:
        # Pas de changement, maintenir les valeurs actuelles
        gx = gyro_x
        gy = gyro_y
        gz = gyro_z
    
        """
        gx = 50.0
        gy = 25.0
        gz = 15.0
        """

    

# Initialiser pygame et PyOpenGL
def main(filename):
    video_flags = OPENGL|DOUBLEBUF
    pygame.init()
    screen = pygame.display.set_mode((640,480), video_flags)
    pygame.display.set_caption("Press Esc to quit")
    resize(640,480)
    init()
    frames = 0
    ticks = pygame.time.get_ticks()

    
    #glTranslatef(0.0, 0.0, -10)  # Recule la caméra
    #glScalef(0.1, 0.1, 0.1)  # Réduit l'objet

    vertices, textures, normals, faces = load_obj(filename)

    
    
    #textures_objet = load_texture("monkey.jpg")
    
    while True:
        
        event = pygame.event.poll()
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()  #* quit pygame properly
            break  

        #glRotatef(1, 3, 1, 1) rotation


        read_data()
        
        draw_obj(vertices, textures, normals, faces)
        
        pygame.display.flip()
        frames = frames+1
        
    
    print ("fps:  %d" % ((frames*1000)/(pygame.time.get_ticks()-ticks)))
    


if __name__ == "__main__":
    main("monkey.obj")
