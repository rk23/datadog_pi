import pigpio
import time
from datadog import initialize, api

pi = pigpio.pi()

RED = 17
GREEN = 22
BLUE = 24

options = {
    'api_key': '51b38a446a3d1e0f416a0ac5f872309a',
    'app_key': 'eddbc05f9524a136e03bbf00f89b573cc5876578'
}

ignore_monitors = ('[Auto] Clock in sync with NTP',  'Connections to DB are present')
monitors_state = []
led_state = {RED: 0,GREEN: 100,BLUE: 0}

initialize(**options)

def change_color(color, brightness):
    if brightness > led_state[color]:
        led_state[color] = led_state[color] + 5
        pi.set_PWM_dutycycle(color, led_state[color])
        time.sleep(.025)
        change_color(color, brightness)
    elif brightness < led_state[color]:
        led_state[color] = led_state[color] - 5
        pi.set_PWM_dutycycle(color, led_state[color])
        time.sleep(.025)
        change_color(color, brightness)
    else:
        pi.set_PWM_dutycycle(color, brightness)

#Startup with blue
change_color(RED, 0)
change_color(GREEN, 0)
change_color(BLUE, 240)
time.sleep(5)

def call_api():
    res = api.Monitor.get_all()
    for monitor in res:
        name = monitor['name']
        state = monitor['overall_state']
        if name not in ignore_monitors:
            monitors_state.append(state)

    update_state = 'green'

    for state in monitors_state:
        if state == 'Warn':
            update_state = 'yellow'
        if state == 'Alert':
            update_state = 'red'
            break

    if update_state == 'yellow':
        change_color(RED, 150)
        change_color(GREEN, 30)
        change_color(BLUE, 0)
    elif update_state == 'red':
        change_color(RED, 255)
        change_color(GREEN, 0)
        change_color(BLUE, 0)
    else:
        change_color(RED, 0)
        change_color(BLUE, 0)
        change_color(GREEN, 200)

if __name__ == '__main__':
    while True:
        try:        
            call_api()
        except Exception as e:
            print(e)
        time.sleep(30)
        change_color(RED, 0)
        change_color(GREEN, 0)
        change_color(BLUE, 200)

