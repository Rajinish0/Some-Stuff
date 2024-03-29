import math,copy
import numpy as np
from functools import reduce

class Vector():
    def __init__(self,*args):
        self.elems = [i for i in args]

    @property    
    def x(self):
        return self.elems[0]
    @property
    def y(self):
        return self.elems[1]
    @property
    def z(self):
        return self.elems[2]
    @property
    def npV(self):
        return np.array([*self.elems]).reshape(-1,1)
    


    @x.setter
    def x(self,val):
        self.elems[0] = val
    @y.setter
    def y(self,val):
        self.elems[1] = val
    @z.setter
    def z(self,val):
        self.elems[2] = val



    def normalized(self):
        magnitude = self.GetMagnitude()
        if not magnitude == 0:
            args = [(elem/magnitude) for elem in self.elems]
            return Vector(*args)
        else:
            return Vector(0,0)            

    def __repr__(self):
        return ('Vector {}'.format(self.elems))

    def __getitem__(self,ind):
        return self.elems[ind]

    def __len__(self):
        return len(self.elems);

    def __add__(self,b):
        if not isinstance(b,Vector):
            raise Exception("Gotta be a vector {}".format(b))
        try:
            return Vector(*[(self[i] + b[i]) for i in range(len(self))])
        except:
            raise Exception("dims don't match {}d and {}d".format(len(self),len(b)))

    def __iadd__(self, b):
        if not isinstance(b,Vector):
            raise Exception("Gotta be a vector {}".format(b))
        try:
            self.elems = [(self[i] + b[i]) for i in range(len(self))]
        except:
            raise Exception("dims don't match {}d and {}d".format(len(self),len(b)))
        return self

    def __isub__(self, b):
        return self.__iadd__(-b)

    def __imul__(self, v):
        self.elems = [v*(each) for each in self.elems]
        return self



    def applyTransformation(self,mat,return_new=False):
        if not isinstance(mat,Matrix):
            raise Exception('need a matrix.')
        try:
            if len(mat) != len(self.elems):
                raise Exception;

            return Vector(*list((mat.npMAT@self.npV)[:,0]))
            # return Vector(*[mat[i].dot(self) for i in range(mat.shape[1])])
            # return (reduce(lambda x,y :x+y,[(mat[i]*self[i]) for i in range(len(self))]))
        except Exception as err:
            raise Exception(f"{len(self)}d vector with a {len(mat[0])}x{len(mat)} Matrix, '\n\n' {self}\n\n {mat}")

        # self.elems = transformed.elems if not return_new else self.elems
        # return self if not return_new else transformed


    def elem_product(self,b):
        if not isinstance(b,Vector):
            raise Exception('need a vector') 
        return Vector(*[self[i]*b[i] for i in range(len(self))])


    def dot(self,b):
        return reduce(lambda x,y :x+y,[self[i]*b[i] for i in range(len(self))])


    def SetMag(self,mag):
        new = self.normalized()*mag
        self.elems = new.elems
        return self

    def heading(self,deg=True):
        norm = self.normalized()
        return np.angle(np.array([complex(norm.x,norm.y)]),deg)[0]

    ##2D rotation
    def rotate(self,center,angle,return_new=False):
        '''can define a rotation matrix for this um [[cosx, -sinx],
                                                     [sinx,cosx]] * [[x]]
                                                                     [y]]'''
        elemsOrig = self.elems[:]
        self.elems = [self[i]-center[i] for i in range(len(self))]
        #newX = self.x*math.cos(math.radians(angle)) - self.y*math.sin(math.radians(angle))
        #newY = self.y*math.cos(math.radians(angle)) + self.x*math.sin(math.radians(angle))
        rotationMatrix = Matrix([[math.cos(math.radians(angle)),-1*math.sin(math.radians(angle))],
                                [math.sin(math.radians(angle)),math.cos(math.radians(angle))]])
        transformation = self.applyTransformation(rotationMatrix)
        self.elems = [center[i]+transformation[i] for i in range(len(self))]
        returnElems = self.elems[:]
        self.elems = elemsOrig if return_new else returnElems
        return Vector(*returnElems)


    def RotationOnX(self,angle):
        m = Matrix([[1,0,0],
                [0,math.cos(math.radians(angle)),-math.sin(math.radians(angle))],
                [0,math.sin(math.radians(angle)),math.cos(math.radians(angle))]])
        return m
    def RotationOnY(self,angle):
        m = Matrix([
                [math.cos(math.radians(angle)),0,-math.sin(math.radians(angle))],
                [0,1,0],
                [math.sin(math.radians(angle)),0,math.cos(math.radians(angle))]
                ])  
        return m
    def RotationOnZ(self,angle):
        m = Matrix([
                [math.cos(math.radians(angle)),-math.sin(math.radians(angle)),0],
                [math.sin(math.radians(angle)),math.cos(math.radians(angle)),0],
                [0,0,1]
                ])
        return m

    ##3D rotations
    def rotation(self, angle, center, axis='x', return_new=True, rotateCenter=True):
        if type(axis) == Vector:
            return self.RotationAboutAxis(angle, center, axis, return_new, rotateCenter)
        elif axis == 'x':
            return self.RotationX(angle, center, return_new)
        elif axis == 'y':
            return self.RotationY(angle, center, return_new)
        elif axis == 'z':
            return self.RotationZ(angle, center, return_new)
        else:
            raise Exception(f'Undefined axis {axis}')

    def RotationX(self,angle,center,return_new=True):
        return self.Gen3dRotation(self.RotationOnX(angle),center,return_new) if angle != 0 else self.returnSelf(return_new)
    def RotationY(self,angle,center,return_new=True):
        return self.Gen3dRotation(self.RotationOnY(angle),center,return_new) if angle != 0 else self.returnSelf(return_new)
    def RotationZ(self,angle,center,return_new=True):
        return self.Gen3dRotation(self.RotationOnZ(angle),center,return_new) if angle != 0 else self.returnSelf(return_new)
    def RotationAboutAxis(self, angle, center, axis,return_new=True, rotateCenter=True):
        if angle == 0:
            return self.returnSelf(return_new)
        assert len(self.elems) == 3;
        theta = Vector(axis.z, axis.x).heading()
        phi = Vector(np.sqrt(axis.z**2 + axis.x**2), axis.y).heading()
        #axis = axis.elem_product(Vector(0, -1,-1))
        # theta = math.atan(axis.x/axis.z)*180/math.pi if not axis.z == 0 else 90*(-1 if axis.x < 0 else 1)
        # phi = math.atan(axis.y/np.sqrt(axis.z**2 + axis.x**2))*180/math.pi if not (axis.z == 0 and axis.x == 0) else 90*(-1 if axis.y < 0 else 1)
        theta = 0 if (axis.x == 0 and axis.z == 0) else theta

        if rotateCenter:
            center = center.RotationY(theta, Vector(0,0,0), return_new=True)
            center.RotationX(phi,Vector(0,0,0), return_new=False)
            # center = center.Gen3dRotation(self.RotationOnY(-theta), Vector(0,0,0), return_new=True)
            # center = center.Gen3dRotation(self.RotationOnX(-phi), Vector(0,0,0), return_new=True)

        v = self.RotationY(theta, Vector(0,0,0), return_new)
        v = v.RotationX(phi, Vector(0,0,0), return_new)
        # print(axis.rotation(-theta,Vector(0,0,0)).rotation(-phi, Vector(0,0,0)), theta, phi)

        v = v.RotationZ(angle, center, return_new)

        v = v.RotationX(-phi, Vector(0,0,0), return_new)
        v = v.RotationY(-theta, Vector(0,0,0), return_new)
        return v



    def returnSelf(self,return_new):
        return Vector(*self.elems) if return_new else self

    def Gen3dRotation(self,mat,center,return_new = True):
        origElems = copy.copy(self.elems)
        self.elems = [self[i]-center[i] for i in range(len(self))]

        transformation = self.applyTransformation(mat)
        self.elems = [center[i]+transformation[i] for i in range(len(self))]
        rotated = self.elems


        self.elems = origElems if return_new else self.elems
        return self if not return_new else Vector(*rotated)



    def GetMagnitude(self, sqrt=True):
        mag = (sum([pow(elem,2) for elem in self.elems]))
        return math.sqrt(mag) if sqrt else mag

    def __mul__(self,scl):
        if isinstance(scl,Vector):
            return self.dot(scl)
        return Vector(*[self[i]*scl for i in range(len(self))])

    def __rmul__(self,scl):
        return self.__mul__(scl)
    #__rmul__= __mul__



    def __truediv__(self,scl):
        return Vector(*[self[i]/scl for i in range(len(self))])


    def __sub__(self,b):
        res = self.__add__(-1*b)
        return res

    def __eq__(self,other):
        return reduce(lambda x,y: x and y, [self[i] == other[i] for i in range(len(self))]) if other is not None else False

    def __neg__(self):
        return Vector(*[-each for each in self.elems])
        #self.elems = [-each for each in self.elems]
        return self


    @staticmethod
    def up():
        return Vector(0,-1)
    @staticmethod
    def GetDist(v1,v2):
        return math.sqrt(reduce(lambda x,y: x+y, [pow(v1[i]-v2[i],2) for i in range(len(v2))]))
    @staticmethod
    def down():
        return Vector(0,1)
    @staticmethod
    def left():
        return Vector(-1,0)
    @staticmethod
    def right():
        return Vector(1,0)


## I PROBABLY SHOULD MAKE THIS COMPATIBLE WITH NUMPY..
class Matrix():
    def __init__(self,twoDList):
        self.mat = []

        if type(twoDList[0]) == list or type(twoDList) == np.ndarray:
            try:
                validLen = len(twoDList[0])
            except:
                validLen = 1


            self.npMAT = np.array(twoDList)
            try:
                twoDList= [list(x) for x in self.npMAT.T]
            except:
                twoDList = [[x] for x in self.npMAT.T]


            prev = None
            for each in twoDList:
                if prev is not None and len(each) != len(prev):
                    raise Exception('dims don\'t match {}d and {}d.'.format((prev),(each)))
                v = Vector(*each)
                self.mat.append(v)
                prev = v

        elif type(twoDList[0]) == Vector:
            self.mat = twoDList
            self.npMAT = Matrix.GenerateNpMat(twoDList)
            assert reduce((lambda x,y: x and y), [(type(each) == Vector) for each in twoDList])

        else:
            raise Exception(f'invalid. {type(twoDList[0])}')


    @property
    def shape(self):
        return Vector(len(self.mat[0]),len(self.mat))
    
    def __repr__(self):
        return f'MATRIX {self.mat}'

    def __mul__(self,scl):
        return Matrix([self[i]*scl for i in range(len(self))])
    __rmul__ = __mul__

    def __add__(self,b):
        return Matrix([self[i]+b[i] for i, each in enumerate(self)])

    def __sub__(self,b):
        return self + (b*-1)

    def __getitem__(self,i):
        return self.mat[i]

    def __len__(self):
        return len(self.mat)
    
    def inv(self):
        return Matrix(np.linalg.inv(self.npMAT))

    def applyTransformation(self,mat):
        if type(mat) != Matrix:
            mat = Matrix(mat)
        try:
            return Matrix([self[i].applyTransformation(mat) for i in range(len(self))])
        except:
            raise Exception(f"{len(self)}x{len(self[0])} with {len(mat)}x{len(mat[0])}.")



    def calcDeterminent(self,mat=None):
        mat = self.npMAT if mat is None else mat
        assert type(mat) == np.ndarray

        if not reduce(lambda x,y: x == y, [each for each in mat.shape]):
            raise Exception(f"NOT A SQUARE MATRIX: {mat.shape}")

        if len(mat[0]) == 1:
            return mat.item()


        det = 0
        for i in range(len(mat[0])):
            num = mat[0][i]
            nMat = mat[1:]
            rMat = np.c_[nMat[:,:i],nMat[:,i+1:]]
            det += pow(-1,1+i+1) * num * self.calcDeterminent(rMat)
        return det

    @staticmethod
    def GenerateNpMat(twoDList):
        return np.array([each.elems for each in twoDList]).T
