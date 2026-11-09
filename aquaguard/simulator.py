def simulate_savings(rate_l_per_hour: float, current_delay_hours: float, target_delay_hours: float):
    if rate_l_per_hour<0 or current_delay_hours<0 or target_delay_hours<0:
        raise ValueError("Inputs must be non-negative")
    current=rate_l_per_hour*current_delay_hours
    target=rate_l_per_hour*target_delay_hours
    return {"current_loss_l":round(current,2),"target_loss_l":round(target,2),"avoided_l":round(max(0,current-target),2)}
