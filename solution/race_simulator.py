import sys
import json

def calculate_race_times(race_config, strategies):
    base_lap_time = race_config['base_lap_time']
    pit_time = race_config['pit_lane_time']
    temp = race_config['track_temp'] - 25.0
    total_laps = race_config['total_laps']
    
    off_S, off_M, off_H = -1.3345068342286626, -0.3480072116681674, 0.4368717632845135
    r_S, r_M, r_H = 1.46998001800897, 0.7518947887866986, 0.3819159775774934
    t_S, t_M, t_H = 0.03907148270950899, 0.018870989625847285, 0.008642486696072316
    
    total_times = {}
    
    for pos, strat in strategies.items():
        driver_id = strat['driver_id']
        pit_stops = sorted(strat.get('pit_stops', []), key=lambda x: x['lap'])
        pits = len(pit_stops)
        
        current_tire = strat['starting_tire']
        current_age = 1
        pit_idx = 0
        
        time = pits * pit_time
        
        for lap in range(1, total_laps + 1):
            if current_tire == 'SOFT':
                off = off_S
                d = max(0, current_age - 10)
                deg = r_S * d + t_S * d * temp
            elif current_tire == 'MEDIUM':
                off = off_M
                d = max(0, current_age - 20)
                deg = r_M * d + t_M * d * temp
            else:
                off = off_H
                d = max(0, current_age - 30)
                deg = r_H * d + t_H * d * temp
                
            time += (base_lap_time + off + deg)
            
            if pit_idx < len(pit_stops) and lap == pit_stops[pit_idx]['lap']:
                current_tire = pit_stops[pit_idx]['to_tire']
                current_age = 1
                pit_idx += 1
            else:
                current_age += 1
                
        total_times[pos] = (time, driver_id)
        
    def sort_key(item):
        pos_str, (time, d_id) = item
        pos_int = int(pos_str.replace('pos', ''))
        return (time, pos_int)
        
    sorted_drivers = sorted(total_times.items(), key=sort_key)
    return [d_id for pos_str, (time, d_id) in sorted_drivers]

def main():
    try:
        input_data = sys.stdin.read()
        if not input_data.strip():
            print("{}")
            return
            
        race = json.loads(input_data)
        race_id = race.get('race_id', 'UNKNOWN')
        
        finishing_positions = calculate_race_times(race['race_config'], race['strategies'])
            
        output = {
            "race_id": race_id,
            "finishing_positions": finishing_positions
        }
        
        sys.stdout.write(json.dumps(output))
        sys.stdout.flush()
        
    except Exception as e:
        import traceback
        sys.stdout.write(json.dumps({"error": str(e), "traceback": traceback.format_exc()}))
        sys.stdout.flush()

if __name__ == '__main__':
    main()
