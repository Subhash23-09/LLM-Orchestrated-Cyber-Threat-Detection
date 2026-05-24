with open('ddos_simulation.log', 'w') as f:
    for i in range(1, 1501):
        f.write(f"Jan 04 16:00:01 web-server-01 custom_app[1234]: UNKNOWN_FLOOD_EVENT from 45.33.22.11 - seq={i}\n")
