from itertools import permutations, chain, combinations
import math

class Drone:
    """
    Drone class representing a delivery drone
    Attributes:
    - name (str): name of the drone
    - capacity (int): maximum weight capacity of the drone
    - speed (int): speed of the drone
    - battery (int): current battery life of the drone
    - max_battery (int): maximum battery life of the drone
    - bcr_rate (int): battery consumption rate of the drone wrt payload
    - charge_rate (int): rate at which the drone recharges its battery
    - drain_rate (int): rate at which the drone's battery drains
    - current_packages (List[Package]): list of packages currently loaded on the drone
    - coordinate (Coordinate): current location of the drone
    """

    def __init__(self, name, capacity, speed, battery, bcr, charge_rate, drain_rate,height_rate=1.5,altitude=10,takeoff_rate = 1.5):
        self.name = name
        self.capacity = capacity
        self.speed = speed
        self.battery = battery
        self.max_battery = battery
        self.bcr_rate = bcr
        self.charge_rate = charge_rate
        self.drain_rate = drain_rate
        self.current_packages = []
        self.coordinate = Coordinate(0, 0,0)
        self.height_rate = height_rate
        self.altitude = altitude
        self.takeoff_rate = takeoff_rate
        self.emergency_amount_battery = 100

    def current_load(self):
        """Returns the current weight load on the drone"""
        load = 0
        for package in self.current_packages:
            load += package.weight
        return load

    def unload_package(self, package):
        """Removes a package from the drone's current packages"""
        if package in self.current_packages:
            self.current_packages.remove(package)
    
    def update_location(self, new_coordinate):
        """Updates the location of the drone"""
        self.coordinate = new_coordinate

    def charge(self, time):
        """Charges the drone for a given time"""
        charge_amount = self.charge_rate * time
        new_battery = self.current_battery() + charge_amount
        self.update_battery(new_battery)
        return time

    def current_battery(self):
        """Returns the current battery life of the drone"""
        return self.battery

    def update_battery(self, battery):
        """Updates the battery life of the drone"""
        self.battery = battery
    
    def current_location(self):
        """Returns the current location of the drone"""
        return self.coordinate

    def current_capacity(self):
        """Returns the remaining capacity of the drone"""
        return self.capacity-self.current_load()
    
    def load(self, packages):
        """Loads packages onto the drone"""
        for package in packages:
            if package.weight <= self.current_capacity():
                self.current_packages.append(package)
            else:
                raise Exception("Package too heavy")
        
    def deliver(self, package):
        """Delivers a package by removing it from the drone's current packages"""
        if package in self.current_packages:
            self.current_packages.remove(package)
        print("Package delivered")
        
    def set_altitude(self,altitude):
        self.altitude = altitude
        
    def current_height(self):
        return self.coordinate.z
    def set_height(self,height):
        current_coordinate = self.current_location()
        self.update_location(self, Coordinate(current_coordinate.x,current_coordinate.y,height))
    
    def takeoff(self,height):
        if height < self.current_height():
            Exception('Takeoff height less than current height')
        current_height = self.current_height()
        diff_height = height - current_height
        required = diff_height * (1+takeoff_rate * self.current_load()) * drain_rate
        if self.current_battery()<required:
            Exception('Not enough battery to takeoff')
        self.set_height(height)
        return required

    def land(self,height = 0):
        if height>self.current_height():
            Exception('Height higher than current for landing')
            
        required = abs(self.current_height -height ) * (1+self.current_load() * height_rate) *drain_rate
        if self.current_battery() < required:
            Exception('Not enough battery to land safely')
        self.set_height(height)
        return required
            
        


class Coordinate:
    """
    Coordinate class representing the x, y position of drone location and delivery location
    Attributes:
    - x (int): x coordinate
    - y (int): y coordinate
    """

    def __init__(self, x, y,z=0):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'{self.x, self.y,self.z}'
    
    def distance(first_coordinate, second_coordinate):
        """Calculates the Euclidean distance between two coordinates"""
        x_distance = (second_coordinate.x - first_coordinate.x)**2
        y_distance = (second_coordinate.y - first_coordinate.y)**2

        return (x_distance+y_distance)**0.5

    def slope(first_coordinate, second_coordinate):
        """Calculates the slope between two coordinates"""
        y_diff = second_coordinate.y - first_coordinate.y
        x_diff = second_coordinate.x - first_coordinate.x
        if x_diff==0:
            return 0
        
        return y_diff/x_diff

    def calc_distance(self, coordinate):
        """Calculates the Euclidean distance between current coordinates of the drone and coordinates of location"""
        return self.distance(self.coordinate, coordinate)

    def update(self, coordinate):
        """Updates the coordinates of the drone"""
        self.x = coordinate.x
        self.y = coordinate.y
        self.z = coordinate.z

    def magnitude(self):
        return (self.x**2 + self.y**2)**0.5
    
    def dot_product(first_coordinate, second_coordinate):
        sx = first_coordinate.x * second_coordinate.x
        sy = first_coordinate.y * second_coordinate.y
        return sx+sy

    
class Package:
    """
    Package class representing a package to be delivered
    Attributes:
    - ID (int): unique ID of the package
    - location (Coordinate): location of the package
    - weight (int): weight of the package
    - quantity (int): quantity of the same item being delivered
    - priority (int): priority level of the package delivery
    """

    def __init__(self, ID, location, weight, quantity, priority):
        self.ID = ID
        self.location = location
        self.weight = weight*quantity
        self.quantity = quantity
        self.priority = priority

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'P({self.weight})'
class Delivery:
    """
    Delivery class representing a drone delivery
    Attributes:
    - drone (Drone): drone that will be delivering packages
    - packages (List[Package]): list of packages to be delivered in current delivery
    - remaining_packages (List[Package]): current list of packages to be delivered in current delivery
    - base (Coordinate): initial coordinates of the drone
    """

    def __init__(self, drone, packages, env, setenv=False):
        self.drone = drone
        self.base = Coordinate(0, 0,0)
        self.HEIGHT_CONSTANT = 1000
        self.BCR_CONSTANT = 1000
        self.priority_dict = {'N':10e7, 'F': 20, 'U': 10}
        self.packages = packages
        self.remaining_packages = packages
        self.env = env
        self.setenv = setenv
        self.filter_packages()
        self.best_path = self.get_best_path(self.remaining_packages.copy())
        
       
                
       
    
    def order(self):
        """"""
        weight_list = []
        for package in self.packages:
            weight_list.append(package.weight)
    
    
    def all_possible_paths(self,packages):
        char = 'H'
        packages_list = packages
        for i in range(len(packages)-1):
            packages_list.append(char)

        all_path_list = list(permutations(packages_list))
        all_path_list = [list(path) for path in all_path_list]
        all_path_list = [self.strip_array(path,char) for path in all_path_list]
        all_path_list = self.remove_duplicates(all_path_list)
##        print("PRINTING ALL STRING PATHS")
##    
##        print(all_path_list)
##        print("DONE")
##        print(len(all_path_list))
        
        return self.path_maker(all_path_list,char)
        
    def remove_duplicates(self,all_paths):
        new_paths = []
        for path in all_paths:
            if path in new_paths:
                continue
            else:
                new_paths.append(path)
        return new_paths
        
    
    def strip_lr(self,lst, char):
        i = 0
        j = len(lst)-1
        while i<j:
            if lst[i]==char:
                i+=1
            else:
                break
        while j>0:
            if lst[j]==char:
                j-=1
            else:
                break
        return lst[i:j+1]

    def strip_left(self,lst,char):
        i = 0
        while i<len(lst):
            if lst[i]==char:
                i+=1
            else:
                break
        return lst[i:]

    def strip_array(self,lst,char):
        lst = self.strip_lr(lst,char)
        i=0
        while i<len(lst):
            if lst[i]==char:
                lst = lst[:i+1] + self.strip_left(lst[i+1:],char)
            i+=1
        return lst
                

    def path_maker(self,all_paths,char):
        paths = []
        current_path = []

        for i in range(len(all_paths)):
            pooled_path = []
            j=0
            while j<len(all_paths[i]):
                if all_paths[i][j]==char:
                    current_path.append(pooled_path)
                    pooled_path = []
                    while all_paths[i][j]==char:
                        j+=1
                else:
                    pooled_path.append(all_paths[i][j])
                    
                    j+=1
                    if j==len(all_paths[i]):
                        current_path.append(pooled_path)
            paths.append(current_path)
            current_path = []
##        print(paths)
        return paths

    def simulate_time_and_battery(self, path):
        #print("SIMULATING")
        #print(path)
        time_elapsed = 0
        curr_location = self.base
        i=0
        mx_battery = self.drone.max_battery
        curr_battery = mx_battery
        package_time_list = []    
    
        while i<len(path):
            pool_to_deliver = path[i]
            battery_required = self.battery_required(pool_to_deliver)
            if battery_required+self.drone.emergency_amount_battery>curr_battery:
                
                #print("CHARGING")
                time_elapsed+=self.charge_time(pool_to_deliver,curr_battery)
                curr_battery = battery_required+self.drone.emergency_amount_battery
                #print(f"AFTER SIMULATION CHARGE: {curr_battery}")

            j=0
            while j<len(path[i]):
                current_package = path[i][j]
                time_drain = self.time_drain(curr_location,current_package.location)
                time_elapsed += time_drain
                package_time_list.append([current_package,time_elapsed])
                curr_location = current_package.location
                
                j+=1
                

            base_return_drain = self.time_drain(curr_location,self.base)
            
            time_elapsed+=base_return_drain
            
            curr_location = self.base
            curr_battery -= battery_required
            i+=1
        
        #print(package_time_list)
        #print(f'Final: {curr_battery}')
        return package_time_list
                
                
                
    def path_priority_verifier(self, path):
        
        package_time_list = self.simulate_time_and_battery(path)
        for package_time in package_time_list:
            if self.priority_dict[package_time[0].priority]<package_time[1]:
                return False
        return True

    def path_weight_verifier(self,path):

        for pool in path:
            if Delivery.weight_sum(pool)>self.drone.capacity:
                return False
        return True

    def path_battery_verifier(self, path):

        for pool in path:
            if not self.has_enough_max_battery(pool):
                return False
        return True
        
    def path_battery_required(self,path):
        total_battery_required = 0

        for pool in path:
            total_battery_required += self.battery_required(pool)
        return total_battery_required

    def minimum_battery_path_index(self, all_paths):
    
        min_battery = 10e7
        min_index = 0

        for i in range(len(all_paths)):
            required = self.path_battery_required(all_paths[i])
            if required<min_battery:
                min_battery = required
                min_index = i
        return min_index

    def filtered_paths(self, all_paths):
        i=0
        verified_paths = all_paths.copy()
        while i<len(verified_paths):
            cp = verified_paths[i]
            if self.path_weight_verifier(cp) and self.path_battery_verifier(cp) and self.path_priority_verifier(cp):
                i+=1
                continue
            else:
                del verified_paths[i]

        if len(verified_paths)==0:
            print("No paths satisfy conditions")
        return verified_paths
    def minimum_battery_path(self, all_paths):
        min_index= self.minimum_battery_path_index(all_paths)
        if min_index==None:
            return[]
##        print("HERE")
##        print(all_paths)
##        print(min_index)
##        
        return all_paths[min_index]
                
        
    def get_best_path(self, packages):
        
        all_paths = self.all_possible_paths(packages)
##        print("IN HERE FAM")
##        print(all_paths)
        
        filtered_paths = self.filtered_paths(all_paths)
        print(filtered_paths)
##        for path in filtered_paths:
##            print(self.path_battery_required(path))
##        for path in filtered_paths:
##            print(self.simulate_time_and_battery(path))
        best_path = self.minimum_battery_path(filtered_paths)
        
        return best_path
        
    def weight_sum(package_list):
        """Returns the total weight of packages in a package list"""
        weight_total = 0
        for package in package_list:
            weight_total += package.weight
        return weight_total

    def unload_packages(self, packages):
        """Unloads packages by removing packages from the drone's current packages"""
        for package in packages:
            if package in self.remaining_packages:
                self.remaining_packages.remove(package)
                self.drone.unload_package(package)

    def unload_package(self, package):
        """Unloads a package by removing a package from the drone's current packages"""
        if package in self.remaining_packages:
            self.remaining_packages.remove(package)
            self.drone.unload_package(package)

    def package_order(self, packages):
        """Returns the order in which packages will be delivered"""
        def sub_lists(my_list):
            subs = []
            for i in range(0, len(my_list)+1):
              temp = [list(x) for x in combinations(my_list, i)]
              if len(temp)>0:
                subs.extend(temp)
            subs.remove([])
            
            return subs

        def order_sublist(l):
            """Returns a dictionary in which the possible orders are organised based on the number of packages"""
            # {1: [[10], [11], [12]], 2: [[10, 11], [11, 10]]}
            capacity = self.drone.capacity
            packages_dictionary = dict()

            for temp_list in l:
                if Delivery.weight_sum(temp_list) > capacity:
                    continue

                if not self.has_enough_max_battery(temp_list):
                    continue

                if len(temp_list) not in packages_dictionary:
                    packages_dictionary[len(temp_list)] = [temp_list]
                else:
                    packages_dictionary[len(temp_list)].append(temp_list)

            return packages_dictionary
        
        return order_sublist(sub_lists(packages))

    def height_drain(self, curr_height, nxt_height, curr_load, drain_rate, height_rate,bcr_rate):
        
        return abs(curr_height - nxt_height) * (1 + curr_load * bcr_rate*(1/self.HEIGHT_CONSTANT)) * drain_rate * height_rate

    def battery_drain(self, curr_location, location_to_go, curr_load, drain_rate, bcr_rate,height_rate):
            """Returns the amount of battery consumed by delivering a given list of packages"""
            if curr_location == location_to_go:
                return 0
            
            drain = 0
            height_to_achieve = max(curr_location.z,location_to_go.z) + self.drone.altitude
            #HEIGHT DRAIN
            drain += abs(height_to_achieve - curr_location.z) * (1+curr_load*(1/self.HEIGHT_CONSTANT)*bcr_rate)*drain_rate*height_rate
                        
            if self.setenv==True:
                #ADD EFFECT OF WIND IF ALLOWED
                DV_x = location_to_go.x - curr_location.x
                DV_y = location_to_go.y - curr_location.y
                DV_mag = Coordinate.distance(curr_location,location_to_go)
                if DV_x ==0:
                    direction_vector = Coordinate(0,1)
                else:
                    
                    direction_vector = Coordinate(DV_x/DV_mag, DV_y/DV_mag)

                DP = Coordinate.dot_product(direction_vector, self.env.vec)
               
                wind_factor = math.exp(self.env.ws * self.env.factor * DP * -1)
            else:
                #ELSE NO EFFECT
                wind_factor = 1
                
           
            drain += drain_rate * (1+curr_load*bcr_rate*(1/self.BCR_CONSTANT))* wind_factor * Coordinate.distance(curr_location, location_to_go)
            #LANDING DRAIN
            drain += abs(height_to_achieve - location_to_go.z) * (1+curr_load*(1/self.HEIGHT_CONSTANT)*bcr_rate) * drain_rate*height_rate
            
            
            return drain
        
##    def battery_required(self, packages):
##        """Returns the total amount of battery required for a delivery with a given list of packages"""
##        
##
##        total_drain = 0
##        drain_rate = self.drone.drain_rate
##        bcr_rate = self.drone.bcr_rate
##        required = 0
##        initial_coordinate = Coordinate(0, 0)
##
##        i = -1
##        while i < len(packages)-1:
##            if i < 0:
##                curr = initial_coordinate
##            else:
##                curr = packages[i].location
##                
##            nxt = packages[i+1].location    
##            curr_weight = Delivery.weight_sum(packages[i + 1:])
##            required += self.battery_drain(curr, nxt, curr_weight, drain_rate, bcr_rate)
##            i += 1
##
##        required += self.battery_drain(packages[-1].location, initial_coordinate, 0, drain_rate, bcr_rate)
##        return required

##    def battery_time_required(self,packages):
##        time_elapsed=0
##        total_drain = 0
##        drain_rate = self.drone.drain_rate
##        bcr_rate = self.drone.bcr_rate
##        height_rate = self.drone.height_rate
##        required = 0
##        initial_coordinate = self.base
##
##        i=0
##        curr = initial_coordinate
##        if len(packages)>0:
##            nxt = packages[0].location
##            
##        while i<len(packages):
##            nxt = packages[i].location
##            curr_weight = Delivery.weight_sum(packages[i:])
##            required += self.battery_drain(curr, nxt, curr_weight, drain_rate, bcr_rate,height_rate)
##            curr = nxt
##            i+=1
##        required += self.battery_drain(curr,initial_coordinate, 0, drain_rate, bcr_rate,height_rate)
##        return required

    
    def battery_required(self,packages,debug=False,values=[]):
        
        total_drain = 0
        drain_rate = self.drone.drain_rate
        bcr_rate = self.drone.bcr_rate
        height_rate = self.drone.height_rate
        required = 0
        initial_coordinate = self.base

        i=0
        curr = initial_coordinate
        if len(packages)>0:
            nxt = packages[0].location
            
        while i<len(packages):
            
            nxt = packages[i].location
            
            curr_weight = Delivery.weight_sum(packages[i:])
            required += self.battery_drain(curr, nxt, curr_weight, drain_rate, bcr_rate,height_rate)
            
            curr = nxt
            i+=1
        return_required= self.battery_drain(curr,initial_coordinate, 0, drain_rate, bcr_rate,height_rate)
        
        required+=return_required
        return required

    def time_required(self, packages):
        pass

    def time_drain(self, curr, nxt):
        if curr==nxt:
            return 0
       
        time_elapsed = 0
        speed = self.drone.speed
        takeoff_rate = self.drone.takeoff_rate
        height_to_achieve = max(curr.z, nxt.z) + self.drone.altitude

        time_elapsed += abs(height_to_achieve-curr.z) / takeoff_rate

        distance_covered = Coordinate.distance(curr,nxt)
        time_elapsed+=distance_covered/speed
        

        time_elapsed += abs((height_to_achieve - nxt.z))/takeoff_rate

        return time_elapsed
        
       
        
    def has_enough_battery(self, packages):
        """Checks whether the drone has enough battery to deliver a given list of packages (within the weight limit)"""
        if self.battery_required(packages) + self.drone.emergency_amount_battery> self.drone.current_battery():
            return False
        return True
   
        
    def has_enough_max_battery(self, packages):
        """Checks whether a given list of packages can be delivered even with maximum battery"""
        if self.battery_required(packages) + self.drone.emergency_amount_battery > self.drone.max_battery:
            return False
        return True
    def increment_drain(self, curr_location, location_to_go, curr_load, drain_rate, bcr_rate,height_rate):
        
        """Returns the amount of battery consumed by delivering a given list of packages"""
        
        drain = 0
                
                            
        if self.setenv==True:
            #ADD EFFECT OF WIND IF ALLOWED
            DV_x = location_to_go.x - curr_location.x
            DV_y = location_to_go.y - curr_location.y
            DV_mag = Coordinate.distance(curr_location,location_to_go)
            if DV_x ==0:
                direction_vector = Coordinate(0,1)
            else:
                
                direction_vector = Coordinate(DV_x/DV_mag, DV_y/DV_mag)

            DP = Coordinate.dot_product(direction_vector, self.env.vec)
           
            wind_factor = math.exp(self.env.ws * self.env.factor * DP * -1)
        else:
            #ELSE NO EFFECT
            wind_factor = 1
            

        drain += drain_rate * (1+(1/self.BCR_CONSTANT)*curr_load*bcr_rate)* wind_factor * Coordinate.distance(curr_location, location_to_go)

        return drain
                
    def deliver_drain(self, distance):
        """Returns the battery drained by traveling a distance"""
        total_weight = self.drone.current_load()
        
        return self.drone.drain_rate * (1+total_weight*self.drone.bcr_rate) * distance
    
    def deliver_package(self, package, increment,debug=False):
        """Delivers a package by starting at the current location and dropping it off at the next delivery location
        while providing updates at certain intervals"""
        if not debug:
            print(f'Delivering package {package.ID}')
        time_elapsed = 0
        curr_loc = self.drone.current_location()
        nxt_loc = package.location
        time_drain = self.time_drain(curr_loc,nxt_loc)
        
        current_height = curr_loc.z
        height_to_achieve = max(curr_loc.z,nxt_loc.z) + self.drone.altitude
        height_diff = height_to_achieve - self.drone.current_height()
        height_inc = height_diff/increment
                
        x_diff = nxt_loc.x - curr_loc.x
        y_diff = nxt_loc.y - curr_loc.y
        x_inc = x_diff/increment
        y_inc = y_diff/increment
        curr_battery = self.drone.current_battery()
        if not debug:
            print(f' At {curr_loc}')
            print(f'Battery {curr_battery}')
            print(f'Time elapsed: 0')
            print('-------------------------------------------')
            print("TAKING OFF")

        
        
        for i in range(increment):
            nxt_height = current_height + height_inc
            curr_battery-=self.height_drain(current_height, nxt_height,self.drone.current_load(), self.drone.drain_rate, self.drone.height_rate,self.drone.bcr_rate) 
            current_height = nxt_height
            new_coordinate = Coordinate(curr_loc.x, curr_loc.y, current_height)
            curr_loc = new_coordinate
            time_elapsed += height_inc / self.drone.takeoff_rate
            self.drone.update_location(curr_loc)
            self.drone.update_battery(curr_battery)
            if not debug:
                print(f' At {self.drone.current_location()}')
                print(f'Battery {self.drone.current_battery()}')
                print(f'Time elapsed {time_elapsed}')
                print('-------------------------------------------')
        if not debug:
            print('MOVING TO LOCATION')
        for i in range(increment):
            new_x = curr_loc.x + x_inc
            new_y = curr_loc.y + y_inc
            
            new_coordinate = Coordinate(new_x, new_y,current_height)
            distance_covered = Coordinate.distance(curr_loc, new_coordinate)
            time_elapsed += distance_covered/self.drone.speed
            curr_battery -= self.increment_drain(curr_loc,new_coordinate,self.drone.current_load(),self.drone.drain_rate,self.drone.bcr_rate,self.drone.height_rate)
            curr_loc = new_coordinate
            self.drone.update_location(curr_loc)
            self.drone.update_battery(curr_battery)
            if not debug: 
                print(f' At {self.drone.current_location()}')
                print(f'Battery {self.drone.current_battery()}')
                print(f'Time elapsed {time_elapsed}')
                print('-------------------------------------------')
        if not debug:
            print('LANDING')
        land_height = nxt_loc.z
        current_height = self.drone.current_location().z
        height_diff = abs(land_height - current_height)
        height_inc = height_diff/increment
        
        for i in range(increment):
            nxt_height = current_height - height_inc
            curr_battery-=self.height_drain(current_height, nxt_height,self.drone.current_load(), self.drone.drain_rate, self.drone.height_rate,self.drone.bcr_rate) 
            current_height = nxt_height
            new_coordinate = Coordinate(curr_loc.x, curr_loc.y, current_height)
            curr_loc = new_coordinate
            time_elapsed += height_inc / self.drone.takeoff_rate
            self.drone.update_location(curr_loc)
            self.drone.update_battery(curr_battery)
            if not debug:
                print(f' At {self.drone.current_location()}')
                print(f'Battery {self.drone.current_battery()}')
                print(f'Time elapsed {time_elapsed}')
                print('-------------------------------------------')
        if not debug:
            print('DELIVERING')
        
        self.unload_package(package)
        if not debug:
            print(f'Package {package.ID} delivered')
        
        return time_elapsed
    
    def return_to_base(self,increment,debug=False):
        """Returns to base"""
        if not debug:
            print("RETURNING TO BASE")
        time_elapsed = 0
        
        curr_loc = self.drone.current_location()
        nxt_loc = self.base
        time_drain = self.time_drain(curr_loc,nxt_loc)
        current_height = curr_loc.z
        height_to_achieve = max(curr_loc.z,nxt_loc.z) + self.drone.altitude
        height_diff = abs(height_to_achieve - current_height)
        height_inc = height_diff/increment
                
        x_diff = nxt_loc.x - curr_loc.x
        y_diff = nxt_loc.y - curr_loc.y
        x_inc = x_diff/increment
        y_inc = y_diff/increment
        curr_battery = self.drone.current_battery()
        if not debug:
            print(f' At {curr_loc}')
            print(f'Battery {curr_battery}')
            print(f'Time elapsed: 0')
            print('-------------------------------------------')
            print("TAKING OFF")
        

        
        
        for i in range(increment):
            nxt_height = current_height + height_inc
            curr_battery-=self.height_drain(current_height, nxt_height,self.drone.current_load(), self.drone.drain_rate, self.drone.height_rate,self.drone.bcr_rate) 
            current_height = nxt_height
            new_coordinate = Coordinate(curr_loc.x, curr_loc.y, nxt_height)
            
            curr_loc = new_coordinate
            time_elapsed += height_inc / self.drone.takeoff_rate
            self.drone.update_location(curr_loc)
            self.drone.update_battery(curr_battery)
            if not debug:
                print(f' At {self.drone.current_location()}')
                print(f'Battery {self.drone.current_battery()}')
                print(f'Time elapsed {time_elapsed}')
                print('-------------------------------------------')
        if not debug:
            print('MOVING TO LOCATION')
        for i in range(increment):
            new_x = curr_loc.x + x_inc
            new_y = curr_loc.y + y_inc
            
            new_coordinate = Coordinate(new_x, new_y,current_height)
            
            distance_covered = Coordinate.distance(curr_loc, new_coordinate)
            time_elapsed += distance_covered/self.drone.speed
       
            curr_battery -= self.increment_drain(curr_loc,new_coordinate,self.drone.current_load(),self.drone.drain_rate,self.drone.bcr_rate,self.drone.height_rate)
            curr_loc = new_coordinate
            self.drone.update_location(curr_loc)
            self.drone.update_battery(curr_battery)
            if not debug:
                print(f' At {self.drone.current_location()}')
                print(f'Battery {self.drone.current_battery()}')
                print(f'Time elapsed {time_elapsed}')
                print('-------------------------------------------')
        if not debug:
            print('LANDING')
        land_height = self.base.z
        current_height = self.drone.current_location().z
        height_diff = abs(land_height - current_height)
        height_inc = height_diff/increment
        
        for i in range(increment):
            nxt_height = current_height - height_inc
            curr_battery-=self.height_drain(current_height, nxt_height,self.drone.current_load(), self.drone.drain_rate, self.drone.height_rate,self.drone.bcr_rate) 
            current_height = nxt_height
            new_coordinate = Coordinate(curr_loc.x, curr_loc.y, current_height)
            curr_loc = new_coordinate
            time_elapsed += height_inc / self.drone.takeoff_rate
            self.drone.update_location(curr_loc)
            self.drone.update_battery(curr_battery)
            if not debug:
                print(f' At {self.drone.current_location()}')
                print(f'Battery {self.drone.current_battery()}')
                print(f'Time elapsed {time_elapsed}')
                print('-------------------------------------------')
        
        if not debug:
            print('Reached base')
        
        return time_elapsed

    
    def charge_time(self, packages,curr_battery):
        """Returns the time taken to charge the drone enough to delivery a given list of packages"""
        EMERGENCY_AMOUNT = self.drone.emergency_amount_battery
        battery_required = self.battery_required(packages)
        charge_time = (battery_required-curr_battery + EMERGENCY_AMOUNT)/self.drone.charge_rate
        return charge_time

    def min_battery_index(self, package_lists):
        """Returns the index of the package that consumes the least amount of battery to deliver"""
        min_index = 0
        min_battery = 10e7

        for i in range(len(package_lists)):
            current = self.battery_required(package_lists[i])
            if current < min_battery:
                min_battery = current
                min_index = i
        return min_index
    def final_min_packages(self,packages_list):
        """USES min_battery_index() and min_battery_path() to find the minimum out of all permutations of all poolings of a certain length"""
        min_battery_packages = []
        battery_required = -1
        
        for i in range(len(packages_list)):
            packages = packages_list[i]
            temp_min = self.min_battery_path(packages)
           
            temp_battery_required = self.battery_required(temp_min)
            if battery_required < 0:
                min_battery_packages = temp_min
                battery_required = temp_battery_required
            else:
                if temp_battery_required < battery_required:
                    min_battery_packages = temp_min
                    battery_required = temp_battery_required
        return min_battery_packages
            
            
    def min_battery_path(self, packages):
        """Returns the path that consumes the least amount of battery"""
        permuted_list = list(permutations(packages))
        for i in range(len(permuted_list)):
            permuted_list[i] = list(permuted_list[i])

        k = self.min_battery_index(permuted_list)
        return permuted_list[k]
    
    def filter_packages(self):
        """Filters out the packages that cross the drone's weight limit"""
        i = 0
        while i < len(self.remaining_packages):
            if not self.has_enough_max_battery([self.remaining_packages[i]]) :
                print(f'Package {self.remaining_packages[i].ID} delivery not possible due to battery constraint of drone')
                        
                self.remaining_packages.remove(self.remaining_packages[i])
                continue
            elif self.remaining_packages[i].weight>self.drone.capacity:
                print(f'Package {self.remaining_packages[i].ID} is too heavy')
                self.remaining_packages.remove(self.remaining_packages[i])
                continue
            elif self.time_drain(self.base,self.remaining_packages[i].location) > self.priority_dict[self.remaining_packages[i].priority]:
                print(f'Package {self.remaining_packages[i].ID} not possible in {self.remaining_packages[i].priority} mode')
                self.remaining_packages.remove(self.remaining_packages[i])
                continue
            else:
                i += 1

##    def deliver(self,debug=False):
##        """Delivers all the packages using the optimal route
##        starting with the maximum number of packages that can be delivered"""
##        
##        if len(self.remaining_packages) == 0:
##            print("NOTHING TO DELIVER")
##            return
##        
##        INCREMENT = 1
##        iterations = len(self.packages)
##        total_time = 0
##        
##
##        packages_dict = self.package_order(self.remaining_packages)
##        #print(packages_dict)
##        i = max(packages_dict.keys())
##        to_return_package_list = []
##        to_return_time_list=[]
##        to_return_path_list=[]
##        to_return_battery_list=[]
##        
##        while len(self.remaining_packages) > 0:
##            
##            current_package_lists = packages_dict[i]
##            if debug:
##                print(f'Current package lists: {current_package_lists}')
##               
##
##            list_to_deliver = self.final_min_packages(current_package_lists)
##            self.drone.load(list_to_deliver)
##            
##            if not self.has_enough_battery(list_to_deliver):
##                time_to_charge = self.charge_time(list_to_deliver,self.drone.current_battery())
##                print(f'CHARGING FOR {time_to_charge} minutes')
##                total_time += self.drone.charge(time_to_charge)
##                print(f'AFTER CHARGE: {self.drone.current_battery()}')
##            print(f'Pool to deliver: {list_to_deliver}')
##            for package in list_to_deliver:
##                total_time += self.deliver_package(package, INCREMENT,debug)
##                print(f' Current Battery: {self.drone.battery}')
##                to_return_time_list.append(total_time)
##                to_return_package_list.append(package)
##                to_return_path_list.append([package,package.location])
##                to_return_battery_list.append(self.drone.battery)
##
##            base_return_time = self.return_to_base(INCREMENT,debug)
##            print(f'RETURN TIME: {base_return_time}')
##            total_time += base_return_time
##            to_return_time_list.append(total_time)
##            to_return_battery_list.append(self.drone.battery)
##            to_return_path_list.append(["HOME",self.base])
##            packages_dict = self.package_order(self.remaining_packages)
##
##            if packages_dict.keys():
##                i = max(packages_dict.keys())
##        
##        print("All packages delivered")
##        print(f'Total time taken:{total_time}')
##        print(f'Final battery of drone: {self.drone.battery}')
##        print(to_return_time_list)
##        print(to_return_package_list)
##        print(to_return_path_list)
##        print(to_return_battery_list)
##        total_return_list = []
##        total_return_list.append(to_return_time_list)
##        total_return_list.append(to_return_package_list)
##        total_return_list.append(to_return_path_list)
##        total_return_list.append(to_return_battery_list)
##        return total_return_list

    def deliver(self,debug=False):
        """Delivers all the packages using the optimal route
        starting with the maximum number of packages that can be delivered"""
        path_to_follow = self.best_path.copy()
        if len(path_to_follow)==0:
            print("NOTHING TO DELIVER")
            return    
        INCREMENT = 1
        
        total_time = 0
    
        to_return_package_list = []
        to_return_time_list=[]
        to_return_path_list=[]
        to_return_battery_list=[]
        
        for i in range(len(path_to_follow)):
            pool = path_to_follow[i]

            if not self.has_enough_battery(pool):
                time_to_charge = self.charge_time(pool,self.drone.current_battery())
                print(f'CHARGING FOR {time_to_charge} minutes')
                total_time += self.drone.charge(time_to_charge)
                print(f'AFTER CHARGE: {self.drone.current_battery()}')
            print(f'Pool to deliver: {pool}')
            for package in pool:
                total_time += self.deliver_package(package, INCREMENT,debug)
                print(f' Current Battery: {self.drone.battery}')
                to_return_time_list.append(total_time)
                to_return_package_list.append(package)
                to_return_path_list.append([package,package.location])
                to_return_battery_list.append(self.drone.battery)
            
            base_return_time = self.return_to_base(INCREMENT,debug)
            print(f'RETURN TIME: {base_return_time}')
            total_time += base_return_time
            to_return_time_list.append(total_time)
            to_return_battery_list.append(self.drone.battery)
            to_return_path_list.append(["HOME",self.base])

        print("All packages delivered")
        print(f'Total time taken:{total_time}')
        print(f'Final battery of drone: {self.drone.battery}')
        print(to_return_time_list)
        print(to_return_package_list)
        print(to_return_path_list)
        print(to_return_battery_list)
        total_return_list = []
        total_return_list.append(to_return_time_list)
        total_return_list.append(to_return_package_list)
        total_return_list.append(to_return_path_list)
        total_return_list.append(to_return_battery_list)
        return total_return_list     
##     
##            
##        while len(self.remaining_packages) > 0:
##            
##            current_package_lists = packages_dict[i]
##            if debug:
##                print(f'Current package lists: {current_package_lists}')
##               
##
##            list_to_deliver = self.final_min_packages(current_package_lists)
##            self.drone.load(list_to_deliver)
##            
##            if not self.has_enough_battery(list_to_deliver):
##                time_to_charge = self.charge_time(list_to_deliver,self.drone.current_battery())
##                print(f'CHARGING FOR {time_to_charge} minutes')
##                total_time += self.drone.charge(time_to_charge)
##                print(f'AFTER CHARGE: {self.drone.current_battery()}')
##            print(f'Pool to deliver: {list_to_deliver}')
##            for package in list_to_deliver:
##                total_time += self.deliver_package(package, INCREMENT,debug)
##                print(f' Current Battery: {self.drone.battery}')
##                to_return_time_list.append(total_time)
##                to_return_package_list.append(package)
##                to_return_path_list.append([package,package.location])
##                to_return_battery_list.append(self.drone.battery)
##
##            base_return_time = self.return_to_base(INCREMENT,debug)
##            print(f'RETURN TIME: {base_return_time}')
##            total_time += base_return_time
##            to_return_time_list.append(total_time)
##            to_return_battery_list.append(self.drone.battery)
##            to_return_path_list.append(["HOME",self.base])
##            packages_dict = self.package_order(self.remaining_packages)
##
##            if packages_dict.keys():
##                i = max(packages_dict.keys())
##        
##        print("All packages delivered")
##        print(f'Total time taken:{total_time}')
##        print(f'Final battery of drone: {self.drone.battery}')
##        print(to_return_time_list)
##        print(to_return_package_list)
##        print(to_return_path_list)
##        print(to_return_battery_list)
##        total_return_list = []
##        total_return_list.append(to_return_time_list)
##        total_return_list.append(to_return_package_list)
##        total_return_list.append(to_return_path_list)
##        total_return_list.append(to_return_battery_list)
##        return total_return_list


        
    
class Environment:
    #ENVIRONMENT CLASS
    def __init__(self, ws, wd,factor=0.1):
        self.ws = ws
        self.wd = wd
        self.factor = factor
        self.vec = Coordinate(self.vector()[0],self.vector()[1])
    def vector(self):
        direction = math.radians(self.wd)
        return [math.cos(direction), math.sin(direction)]
        
    
    

def main():
##    p1 = Package(ID=1, location=Coordinate(5, 10,10), weight=10, quantity=1, priority='N')
##    p2 = Package(ID=2, location=Coordinate(5, 11,5), weight=11, quantity=1, priority='N')
##    p3 = Package(ID=3, location=Coordinate(5, 12,5), weight=12, quantity=1, priority='N')
##    p4 = Package(ID=4, location=Coordinate(-25, 26,7), weight=13, quantity=1, priority='N')
##    packages = [p1, p2, p3]
##    
##    p1 = Package(ID=1, location=Coordinate(5, 10,10), weight=10, quantity=1, priority=7)
##    p2 = Package(ID=2, location=Coordinate(5, 10,10), weight=11, quantity=1, priority=7)
    #ptry = Package(ID = 30, location = Coordinate(1,10) , weight = 50, quantity = 1, priority = 7)
    #ptry2 = Package(ID = 20, location = Coordinate(-25,45), weight = 5, quantity = 1, priority = 7)
    #packages = [ptry]
    #p4 = Package(ID=4, location=Coordinate(-25, 45), weight=13, quantity=1, priority=7)
##    packages=[p4]
##    p1 = Package(ID=1, location=Coordinate(5, 10,10), weight=12, quantity=1, priority=7)
##    packages=[p1]
##    packages = [p1,p2]
    pap1 = Package(ID=1, location=Coordinate(5, 10,10), weight=10, quantity=1, priority='N')
    pap2 = Package(ID=2, location=Coordinate(-5, 10,10), weight=11, quantity=1, priority='N')
    pap3= Package(ID=3, location=Coordinate(-10,20,20), weight=12, quantity=1, priority='N')
    pap4 = Package(ID=4, location=Coordinate(-25, 26,7), weight=13, quantity=1, priority='N')
    pap5 = Package(ID=4, location=Coordinate(-15, 11,15), weight=14, quantity=1, priority='N')
    pap6 = Package(ID=4, location=Coordinate(14, 20,10), weight=15, quantity=1, priority='N')
    packages = [pap1,pap2,pap3,pap4,pap5]
    d1 = Drone(name="D1", capacity=40, speed=5, battery=15000, bcr=10, charge_rate=100, drain_rate=50,height_rate = 1.5, altitude = 10, takeoff_rate = 2)
    environ  = Environment(25, -63)
    #print(environ.vec)
    #SET LAST PARAM TO FALSE IF YOU DONT WANT EFFECTS OF WIND, TESTING PURPOSES
    deliv = Delivery(d1, packages,environ,False)
    #test_packages = [[p1],[p2]]
    #deliv.simulate_time_and_battery(test_packages)
    #deliv.deliver(True)
    #print(f'BEST PATH: {deliv.get_best_path(packages)}')
    #print(f'BEST PATH ATTRIBUTE: {deliv.best_path}')
##    print("P1 ALONE")
##    print(deliv.battery_required([p1]))
##    print("P2 ALONE")
##    print(deliv.battery_required([p2]))
##    print(f'POOLED VALUE: {deliv.battery_required([p1,p2])}')
##    print(f'SEPARATE VALUE: {deliv.battery_required([p1]) + deliv.battery_required([p2])}')
##
##    print(f'POOLED VALUE: {deliv.battery_required([p1,p2,p3])}')
##    print(f'SEPARATE VALUE: {deliv.battery_required([p1]) + deliv.battery_required([p2]) + deliv.battery_required([p3])}')
    print(f'BEST PATH: {deliv.best_path}')
    
    #deliv.deliver()
    print(f'BEST PATH TIME: {deliv.simulate_time_and_battery(deliv.best_path)}')
    print(f'REMAINING BATTERY: {deliv.drone.current_battery()}')

main()

"""
UPDATES TO BE MADE:
1. CONSIDER PRIORITY
2. TAKEOFF AND LANDING BATTERY USAGE
3. OPTIMIZATION OF ALGORITHM
4. CONSIDER ALL BATTERY AND TIME
"""
        


    
#Made changes to Battery_Drain formula making it match studies
#Fixed slope error
#Added height
#Drone has a set altitude as a property: it goes this altitude height above its current or destination height first
#Which means it goes straight up first, then to its location, then lands
#Height rate is the extra battery drain during takeoff and landing, affected by weight as well
#If the drone is at (0,0,0) and needs to go to (5,10,10) and it has a altitude property of 20, then it will go upto (10+20) first, then go to (5,10,30) then land (5,10,10)
#If the drone is at (5,10,10) and wants to go to (0,0,0), and it has an altitude of 20, then it will first go to (10+20) 30 altitude, go to (0,0,30) then land (0,0,0)

        
        
                    

            
            
        
                    

