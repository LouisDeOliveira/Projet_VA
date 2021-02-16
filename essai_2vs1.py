import math
import random
import uuid
from collections import defaultdict

import mesa
import tornado, tornado.ioloop
from mesa import space
from mesa.time import RandomActivation
from mesa.visualization.ModularVisualization import ModularServer, VisualizationElement


class Envir(mesa.Model):

    def __init__(self, n_drones, n_target):
        mesa.Model.__init__(self)
        self.space = mesa.space.ContinuousSpace(600, 600, False)
        self.schedule = RandomActivation(self)
        for _ in range(n_drones):
            self.schedule.add(Drone(random.random() * 500, random.random() * 500, 10, int(uuid.uuid1()), self, target=None, guide=None))

        for _ in range(n_target):
            self.schedule.add(Target(random.random() * 500, random.random() * 500, 10, int(uuid.uuid1()), self))


    def step(self):
        self.schedule.step()
        if self.schedule.steps >= 1000:
            self.running = False
    



class ContinuousCanvas(VisualizationElement):
    local_includes = [
        "./js/simple_continuous_canvas.js",
    ]

    def __init__(self, canvas_height=500,
                 canvas_width=500, instantiate=True):
        VisualizationElement.__init__(self)
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.identifier = "space-canvas"
        if (instantiate):
            new_element = ("new Simple_Continuous_Module({}, {},'{}')".
                           format(self.canvas_width, self.canvas_height, self.identifier))
            self.js_code = "elements.push(" + new_element + ");"

    def portrayal_method(self, obj):
        return obj.portrayal_method()

    def render(self, model):
        representation = defaultdict(list)
        for obj in model.schedule.agents:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = ((obj.pos[0] - model.space.x_min) /
                                  (model.space.x_max - model.space.x_min))
                portrayal["y"] = ((obj.pos[1] - model.space.y_min) /
                                  (model.space.y_max - model.space.y_min))
            representation[portrayal["Layer"]].append(portrayal)
        return representation




def distance(agent1, agent2):
    return ((agent2.pos[0]-agent1.pos[0])**2+(agent2.pos[1]-agent1.pos[1])**2)**0.5


class Drone(mesa.Agent):
    def __init__(self, x, y, speed, unique_id: int, model: Envir, target=None, guide=None):
        super().__init__(unique_id, model)
        self.pos = (x, y)
        self.speed = speed
        self.model = model
        self.target = target
        self.guide = guide

    def portrayal_method(self):
        if self.target == None and self.guide == None:
            color = "blue"
            r = 3
            portrayal = {"Shape": "circle",
                        "Filled": "true",
                        "Layer": 1,
                        "Color": color,
                        "r": r}
            return portrayal
        elif self.target != None:
            color = "green"
            r = 3
            portrayal = {"Shape": "circle",
                        "Filled": "true",
                        "Layer": 1,
                        "Color": color,
                        "r": r}
            return portrayal
        elif self.guide != None:
            color = "black"
            r = 3
            portrayal = {"Shape": "circle",
                        "Filled": "true",
                        "Layer": 1,
                        "Color": color,
                        "r": r}
            return portrayal


    def wander(self):
        if self.guide == None and self.target == None:
            r = random.random() * math.pi * 2
            new_x = max(min(self.pos[0] + math.cos(r) * self.speed, self.model.space.x_max), self.model.space.x_min)
            new_y = max(min(self.pos[1] + math.sin(r) * self.speed, self.model.space.y_max), self.model.space.y_min)
            
            return new_x, new_y
        
        elif self.target != None:
            t_agent = self.target
            d = distance(self, t_agent)
            cosr = (t_agent.pos[0] - self.pos[0])/d
            sinr = (t_agent.pos[1] - self.pos[1])/d

            new_x = max(min(self.pos[0] + cosr * self.speed,
                            600), 0)
            new_y = max(min(self.pos[1] + sinr * self.speed,
                            600), 0)
        
        elif self.guide != None:
            t_guide = self.guide
            t_agent = t_guide.target
            d = distance(self, t_agent)
            cosr = (t_agent.pos[0] - self.pos[0])/d
            sinr = (t_agent.pos[1] - self.pos[1])/d

            new_x = max(min(self.pos[0] + cosr * self.speed,
                            600), 0)
            new_y = max(min(self.pos[1] + sinr * self.speed,
                            600), 0)

    def step(self, d=100):
        self.pos = self.wander()
        if self.target == None and self.guide == None:
            other_agents = self.model.schedule.agents
            
            for agent in other_agents:
                if type(agent) == Target:
                    dist = ((agent.pos[0]-self.pos[0])**2+(agent.pos[1]-self.pos[1])**2)**0.5
                    if dist < d:
                        self.target = agent
                if type(agent) == Drone:
                    if agent.target != None:
                        self.guide = agent
    


            

class Target(mesa.Agent):
    def __init__(self, x, y, speed, unique_id: int, model: Envir):
        super().__init__(unique_id, model)
        self.pos = (x, y)
        self.speed = speed
        self.model = model

    def portrayal_method(self):
        color = "red"
        r = 3
        portrayal = {"Shape": "circle",
                    "Filled": "true",
                    "Layer": 1,
                    "Color": color,
                    "r": r}
        return portrayal

    def wander(self):
        r = random.random() * math.pi * 2
        new_x = max(min(self.pos[0] + math.cos(r) * self.speed, self.model.space.x_max), self.model.space.x_min)
        new_y = max(min(self.pos[1] + math.sin(r) * self.speed, self.model.space.y_max), self.model.space.y_min)
        
        return new_x, new_y

    def step(self):
        self.pos = self.wander()
    



def run_single_server():
    server = ModularServer(Envir,
                           [ContinuousCanvas()],
                           "Envir",
                           {"n_drones": 5,"n_target":1})
    server.port = 8521
    server.launch()
    tornado.ioloop.IOLoop.current().stop()


if __name__ == "__main__":
    run_single_server()
