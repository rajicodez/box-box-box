import sys
import json

def calculate_race_times(race_config, strategies):
    base_lap_time = race_config['base_lap_time']
    pit_time = race_config['pit_lane_time']
    temp = race_config['track_temp'] - 25.0
    total_laps = race_config['total_laps']
    
    # Exact physical constants derived via Gradient Descent optimization
    off_S, off_M, off_H = -1.1799867, -0.2032529, 0.592793
    deg_S, deg_M, deg_H = 1.4947913, 0.75324184, 0.3712976
    t_S, t_M, t_H = 0.04588488, 0.02319887, 0.01481824
    
    total_times = {}
    
    for pos, strat in strategies.items():
        driver_id = strat['driver_id']
        pit_stops = sorted(strat.get('pit_stops', []), key=lambda x: x['lap'])
        pits = len(pit_stops)
        
        current_tire = strat['starting_tire']
        current_age = 1
        pit_idx = 0
        
        # Start with pit penalty time
        time = pits * pit_time
        
        for lap in range(1, total_laps + 1):
            if current_tire == 'SOFT':
                off = off_S
                d = max(0, current_age - 10) # 10 lap cliff
                deg = deg_S * d + t_S * d * temp
            elif current_tire == 'MEDIUM':
                off = off_M
                d = max(0, current_age - 20) # 20 lap cliff
                deg = deg_M * d + t_M * d * temp
            else:
                off = off_H
                d = max(0, current_age - 30) # 30 lap cliff
                deg = deg_H * d + t_H * d * temp
                
            time += (base_lap_time + off + deg)
            
            if pit_idx < len(pit_stops) and lap == pit_stops[pit_idx]['lap']:
                current_tire = pit_stops[pit_idx]['to_tire']
                current_age = 1
                pit_idx += 1
            else:
                current_age += 1
                
        total_times[pos] = (time, driver_id)
        
    # Stable sort handles identical strategy ties naturally by position integer
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
            return
            
        race = json.loads(input_data)
        race_id = race.get('race_id', 'UNKNOWN')
        
        finishing_positions = calculate_race_times(race['race_config'], race['strategies'])
            
        output = {
            "race_id": race_id,
            "finishing_positions": finishing_positions
        }
        
        sys.stdout.write(json.dumps(output) + "\n")
        sys.stdout.flush()
        
    except Exception as e:
        pass

if __name__ == '__main__':
    main()
