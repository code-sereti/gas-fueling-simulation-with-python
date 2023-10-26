import itertools
import random
import simpy


RANDOM_SEED = 42
STATION_TANK_SIZE = 200    
THRESHOLD = 25             
CAR_TANK_SIZE = 50         
CAR_TANK_LEVEL = [5, 25]
REFUELING_SPEED = 2        
TANK_TRUCK_TIME = 300
T_INTER = [30, 300]        
SIM_TIME = 1000            


def car(name, env, gas_station, station_tank):
    car_tank_level = random.randint(*CAR_TANK_LEVEL)
    print('%6.1f s: %s arrived at gas station' % (env.now, name))
    with gas_station.request() as req:
        
        yield req

        
        fuel_required = CAR_TANK_SIZE - car_tank_level
        yield station_tank.get(fuel_required)
        yield env.timeout(fuel_required / REFUELING_SPEED)

        print('%6.1f s: %s refueled with %.1f liters'
              % (env.now, name, fuel_required))


def gas_station_control(env, station_tank):
    while True:
        if station_tank.level / station_tank.capacity * 100 < THRESHOLD:
            print('%6.1f s: Calling tank truck' % env.now)
            yield env.process(tank_truck(env, station_tank))

        yield env.timeout(10)


def tank_truck(env, station_tank):
    """Arrives at the gas station after a certain delay and refuels it."""
    yield env.timeout(TANK_TRUCK_TIME)
    amount = station_tank.capacity - station_tank.level
    station_tank.put(amount)
    print('%6.1f s: Tank truck arrived and'
          ' refuelled station with %.1f liters' % (env.now, amount))


def car_generator(env, gas_station, station_tank):
    """Generate new cars that arrive at the gas station."""
    for i in itertools.count():
        yield env.timeout(random.randint(*T_INTER))
        env.process(car('Car %d' % i, env, gas_station, station_tank))



print('Gas Station refuelling')
random.seed(RANDOM_SEED)

env = simpy.Environment()
gas_station = simpy.Resource(env, 2)
station_tank = simpy.Container(env, STATION_TANK_SIZE, init=STATION_TANK_SIZE)
env.process(gas_station_control(env, station_tank))
env.process(car_generator(env, gas_station, station_tank))
env.run(until=SIM_TIME)
