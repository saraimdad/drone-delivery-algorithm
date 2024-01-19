
from bruteforcedrone import Drone, Environment, Package, Coordinate, Delivery


class TestDrone():

    def setUp(self):
        self.drone = Drone("Delivery Drone", 100, 20, 100, 5, 10, 2)

    def test_current_load(self):
        package1 = Package("Package 1", 50)
        package2 = Package("Package 2", 30)
        self.drone.load([package1, package2])
        self.assertEqual(self.drone.current_load(), 80)

    def test_unload_package(self):
        package = Package("Package 1", 50)
        self.drone.load([package])
        self.drone.unload_package(package)
        self.assertEqual(len(self.drone.current_packages), 0)

    def test_update_location(self):
        new_coordinate = Coordinate(10, 20, 0)
        self.drone.update_location(new_coordinate)
        self.assertEqual(self.drone.current_location(), new_coordinate)

    def test_charge(self):
        initial_battery = self.drone.current_battery()
        charged_time = self.drone.charge(5)
        self.assertEqual(self.drone.current_battery(), initial_battery + (self.drone.charge_rate * charged_time))

    def test_current_capacity(self):
        package = Package("Package 1", 50)
        self.drone.load([package])
        self.assertEqual(self.drone.current_capacity(), self.drone.capacity - package.weight)

    def test_load(self):
        package1 = Package("Package 1", 50)
        package2 = Package("Package 2", 30)
        self.drone.load([package1])
        with self.assertRaises(Exception):
            self.drone.load([package2])  # Package 2 exceeds the drone's capacity

    def test_deliver(self):
        package = Package("Package 1", 50)
        self.drone.load([package])
        self.drone.deliver(package)
        self.assertEqual(len(self.drone.current_packages), 0)

    def test_set_altitude(self):
        altitude = 50
        self.drone.set_altitude(altitude)
        self.assertEqual(self.drone.altitude, altitude)

    def test_set_height(self):
        height = 30
        self.drone.set_height(height)
        self.assertEqual(self.drone.current_height(), height)


def main():
    td = TestDrone()
    td.setUp()
    td.test_current_load()
    td.test_unload_package()
    td.test_update_location()


if __name__ == "__main__":
    main()
