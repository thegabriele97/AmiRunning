from fitbitPackage import *
from flask import Flask, render_template, redirect, jsonify, request
from ArduinoAPI.AdafruitMotorShield.Adafruit_MotorShield import Adafruit_MotorShield
from ArduinoAPI.AdafruitMotorShield.Adafruit_StepperMotor import Adafruit_StepperMotor
from zwaveapi.zwave import *
from statistics import mean
from gpioAPI import *

import webbrowser
import time
import sys
import cfg
import json
import requests
import threading

user_q = []
threads = {} #Every entry is: thread_name, list(thread, thread_stop_event)
last_data = {} #User to store last running data
last_data_sensor = {}

app = Flask(import_name = __name__, template_folder = './flask/template/')
app._static_folder = "./flask/static/"

@app.route('/')
def index():
    # making dumb requests in order to update some valus
    requests.get('http://%s/system/data/temp' % (cfg.global_configs.public_address))
    requests.get('http://%s/system/data/humidity' % (cfg.global_configs.public_address))

    return render_template(
        "index.html", 
        user_in_queue=len(user_q),
        auth_url=fitbit_api.get_authorize_url()
    )

@app.route('/user/id=<pos>')
def user_id(pos):

    if len(user_q) == 0:
        return redirect("/")
    elif json.loads(requests.get('http://%s/user/%d/is_turn' % (cfg.global_configs.public_address, int(pos))).text)['is_user_turn'] == False:
        try:
            return render_template(
                "index_waiting.html",
                user_pos = pos,
                pos = (user_q.index(search_in_queue(pos)) - int(user_q[0]['user_id']))
            )
        except:
            return redirect('/')
    else:
        fitbit = search_in_queue(pos)['fitbit_obj']
        client : fitbitPackage.fitbit.Fitbit = fitbit.get_auth_client()

        return render_template( 
            "user_id_ok.html",
            user_pos = pos,
            user_name = client.user_profile_get()['user']['fullName'],
            avatar = client.user_profile_get()['user']['avatar150'],
            last_heart_rate = str(getUserBPM()) + ' BPM'
        )

@app.route('/insert_user')
def insert_user():
    fitbit = FitbiAapi(fitbit_api.__client_id__, fitbit_api.__client_secret__)
    fitbit.start_response_poll() #waiting for user authorization on fitbit page

    user_pos = 0 if len(user_q) == 0 else int(user_q[-1]['user_id'])+1
    user_q.append({'user_id': str(user_pos), 'fitbit_obj': fitbit, 'is_running': False}) #inserting user in queue
    return redirect("/user/id=" + str(user_pos))

@app.route('/user/<pos>/leave_queue', methods = ['POST', 'GET'])
def user_leave_queue(pos):

    maintain_after_reload = str(request.data) == "b'0x1'" # if post data is '0x1', the current user (eg. not his turn) will not be removed.
    print("> POST data received: %r (maintain: %r)" % (request.data, maintain_after_reload))

    if request.method == 'GET' or (request.method == 'POST' and (not maintain_after_reload or not user_turn(pos))):
        if len(user_q) > 0 and pos == user_q[0]['user_id']: #stop all threads of current user
            print("> Threads to deactivate: %r" % threads)
            for th_e in dict(threads).values():
                th_e[-1].set()
                #th_e[0].join() #waiting for thread terminating
        
            threads.clear() #after all threads are stopped, they can be removed from list
        
        try:
            user_q.remove(search_in_queue(pos)) #maybe it was removed by a becaon on page exit when use clicked on leave_queue link
        except ValueError:
            pass

    print("> Users still in queue %r" % user_q) #log purpose
    return redirect("/")

@app.route('/user/<pos>/is_turn')
def is_user_turn(pos):

    try:
        remaining_user = (int(pos) - int(user_q[0]['user_id']))
    except:
        remaining_user = None    

    return jsonify(
        user_id = int(pos),
        is_user_turn = user_turn(pos),
        remaining_user = remaining_user
    )

@app.route('/user/<pos>/is_running')
def is_user_running(pos):
    return jsonify(
        user_id = int(pos),
        is_user_running = search_in_queue(pos)['is_running']
    )

@app.route('/system/data/<what>')
def system_data_what(what):
    datas = []

    if what == 'temp':
        getter = get_temp
    elif what == 'humidity':
        getter = get_umi
    elif what == 'luminiscence':
        getter = get_lum
    else:
        return redirect('/')

    get_data = lambda x : getter(str(x))
    for i in range(2, len(get_all_devices().keys()) + 2):
        datas.append(get_data(i))

    avg = lambda x : round(mean(x), 1)
    if what == 'temp':
        args = {'temps': datas, 'avg': avg(datas)}
        last_data_sensor['temp'] = avg(datas)
    elif what == 'humidity':
        args = {'humidities': datas, 'avg': avg(datas)}
        last_data_sensor['humidity'] = avg(datas)
    elif what == 'luminiscence':
        args = {'luminiscences': datas, 'max': int(max(datas))}

    return jsonify(args)

@app.route("/user/<pos>/start_running/<difficult>", methods = ['POST'])
def start(pos, difficult):

    checkpoint = lambda : register_checkpoint(checkpoints)
    neg_dir = lambda dir : Adafruit_StepperMotor.BACKWARD if dir == Adafruit_StepperMotor.FORWARD else Adafruit_StepperMotor.FORWARD

    success = True # CHANGE TO FALSE ONLY IF THERE WAS A PROBLEM DURING THE RUN, LIKE TIMEOUT
    checkpoints = {}

    # SETTING USER IS RUNNING TO TRUE
    search_in_queue(pos)['is_running'] = True

    (th_sleep, e) = create_thread(target=th_timer, kwargs={'timeout1': 6, 'timeout2': 4})# COUNTDOWN WHILE PREPARING THE SYSTEM

    AFMS : Adafruit_MotorShield = Adafruit_MotorShield()
    motor_o : Adafruit_StepperMotor = AFMS.getStepper(200, 1)
    motor_v : Adafruit_MotorShield = AFMS.getStepper(200, 2)
    AFMS.begin() #120 Hz

    motor_o.setSpeed(4000)
    motor_v.setSpeed(4000)

    steps_dif = 0
    if difficult == "easy":
        steps_dif = -12
    if difficult == "hard":
        steps_dif = 12

    steps = get_steps(12)
    print("> %r" % steps)
    steps_dif_steps = steps_dif + steps
    dir = Adafruit_StepperMotor.BACKWARD if steps_dif_steps < 0 else Adafruit_StepperMotor.FORWARD
    steps_dif_abs = abs(steps_dif_steps)
    (th_v_setup, event) = create_thread(th_stepper, kwargs={'motor': motor_v, "dir":dir, 'steps': steps_dif_abs*200, 'loop': False})
    
    steps_dif2 = 0
    if difficult == "easy":
        steps_dif2 = -33
    if difficult == "hard":
        steps_dif2 = 33

    (th_o_setup, event) = create_thread(th_reset_stepper, kwargs={'motor': motor_o, "dir": neg_dir(dir), 'steps': abs(steps_dif2) * 200, 'th_setup': th_v_setup})

    # HERE SHOULD BE ALL READY
    th_sleep.join()
    ledaccess(cfg.global_configs.led_green, True)
    checkpoint() #START CHECKPOINT

    waitPIR(cfg.global_configs.pir_pin_one)
    print("> First checkpoint triggered!")
    checkpoint()

    #SETUP FOR HORIZONTAL MOTOR
    steps2 = get_steps(33)
    print("> %r" % steps2)
    steps_dif_steps2 = steps_dif2 + steps2
    (th_o_resetup, event) = create_thread(th_reset_stepper, kwargs={'motor': motor_o, "dir": Adafruit_StepperMotor.BACKWARD, 'steps': steps2 * 200, 'th_setup': th_o_setup})
    print("> Obstacle distance: %r" % get_distance())

    #RESETS VERTIACL MOTOR
    if dir == Adafruit_StepperMotor.FORWARD:
        dir = Adafruit_StepperMotor.BACKWARD
    else:
        dir = Adafruit_StepperMotor.FORWARD
    (th_v_reset, event) = create_thread(th_reset_stepper, kwargs={'motor': motor_v, "dir": dir, 'steps': steps_dif_abs * 200, 'th_setup': th_o_resetup})

    waitPIR(cfg.global_configs.pir_pin_two)
    print("> Last checkpoint triggered!")
    checkpoint()
    ledaccess(cfg.global_configs.led_green,False)

    #RESETS HORIZONTAL MOTOR
    create_thread(th_reset_stepper, kwargs={'motor': motor_o, "dir": neg_dir(dir), 'steps': abs(steps_dif_steps2) * 200, 'th_setup': th_v_reset})


    # SETTING USER IS RUNNING TO FALSE
    search_in_queue(pos)['is_running'] = False
    last_data['success'] = success
    last_data['checkpoints'] = checkpoints
    time.sleep(0.2) # in order to calm all down

    return jsonify(last_data)

@app.route('/user/<pos>/data_run')
def user_data_run(pos):

    if len(last_data.keys()) == 0:
        return jsonify(available = False)
    
    to_send = {'available': True, 'data': dict(last_data)}
    last_data.clear()
    return jsonify(to_send)


def get_steps(tot_steps):
    giri_battito = (60-(getUserBPM()-60))/(60/tot_steps)
    temp = last_data_sensor['temp']
    if temp < 15:
        perctemp = 0.5
    elif temp < 30:
        perctemp = 1
    else:
        perctemp = 0.75
    
    percumi = (100-last_data_sensor['humidity'])/100
    return giri_battito*perctemp*percumi

def create_thread(target, name = None, kwargs : dict = {}, daemon = True, start = True, array_save = threads):

    if name is None:
        name = 'th' + str(len(array_save))

    event = threading.Event()
    th = threading.Thread(target=target, name=name, args=(name, event), kwargs=kwargs, daemon=daemon)
    
    if start:
        th.start()

    threads[th.getName()] = (th, event)
    return threads[th.getName()]

def th_stepper(name, stopevent : threading.Event, motor : Adafruit_StepperMotor, steps = 50, dir = Adafruit_StepperMotor.BACKWARD, 
    style = Adafruit_StepperMotor.DOUBLE, loop = True, timeout_wait = 0.000001, **kwargs):

    while(not stopevent.wait(timeout_wait)): #while thread is active
        motor.step(steps, dir, style) #do motor steps

        if not loop:
            break

    #here thread is being stopped
    print("> (thread %s) Releasing stepper motor %r .." % (name, motor))
    motor.release() #release current flow on motor to turn it off
    time.sleep(0.5)

def th_reset_stepper(name, stopevent : threading.Event, motor : Adafruit_StepperMotor, steps, dir, th_setup, **kwargs):
    th_setup.join()
    (th1, event) = create_thread(th_stepper, kwargs={'motor': motor, "dir": dir, 'steps': steps, 'loop': False})
    th1.join()

def th_timer(name, stopevent, timeout1 = 1, timeout2 = 1, **kwargs):
    ledaccess(cfg.global_configs.led_red,True)
    time.sleep(timeout1)                            #turns on red for timeout1
    ledaccess(cfg.global_configs.led_red,False)
    ledaccess(cfg.global_configs.led_yellow,True)
    time.sleep(timeout2)                            #turns on yellow for timeout2
    ledaccess(cfg.global_configs.led_yellow,False)


def getUserBPM(pos = '0'):
    try:
        fitbit = user_q[int(pos)]['fitbit_obj']
        client : fitbitPackage.fitbit.Fitbit = fitbit.get_auth_client()
        today_date = get_right_dateFormat()

        #fit_statsHR = client.intraday_time_series('activities/steps', base_date=today_date, detail_level='15min')
        fit_heart = client.intraday_time_series('activities/heart', base_date=today_date, detail_level='1sec')['activities-heart-intraday']['dataset']

        return 91 if len(fit_heart) <= 0 else fit_heart[-1]['value']
    except fitbitPackage.fitbit.exceptions.HTTPTooManyRequests:
        return 91

def search_in_queue(user_id : str, queue = user_q) -> dict:
    for elem in queue:
        if elem['user_id'] == user_id:
            return elem

    return None

def user_turn(pos) -> bool:
    return (len(user_q) != 0 and user_q[0]['user_id'] == pos)

def register_checkpoint(checkpoints : dict, name = None):

    if name is None:
        name = str(len(checkpoints.keys()) - 1)

    if len(checkpoints.keys()) == 0:
        checkpoints['start'] = time.time()
        checkpoints['nCheckpoints'] = 0
        return
    
    checkpoints[name] = seconds2format(time.time() - checkpoints['start'])
    checkpoints['nCheckpoints'] += 1

def seconds2format(seconds):
    '''From seconds to Hours:Minutes;Seconds;SecondsTen'''

    hours = seconds / 3600
    minutes = ((seconds) % 3600) / 60
    seconds = ((seconds) % 3600) % 60

    dec = int((seconds - int(seconds)) * 10)
    return "%02d:%02d:%02d:%d" % (hours, minutes, seconds, dec)


if __name__ == "__main__":
    app.run(
        host=cfg.global_configs.flask_main_address,
        port=cfg.global_configs.flask_main_port, 
        debug=cfg.global_configs.flask_debug
    )