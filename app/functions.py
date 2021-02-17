def imp_to_met(ft, inch, lbs):

    # Inch -> cm
    height = ((ft*12)+ inch) * 2.54
    # lbs -> kg
    weight = lbs * 0.453592

    return height, weight

def tdee_calc(ht, wt, age, act_level, gender):
    #Using Mifflin St. Jeor

    if gender == 'male':
        #Harris Benedict = 66 + (13.7 * wt) + (5 * ht) - (6.8 * age)
        bmr = 10 * wt + 6.25 * ht - 5 * age + 5
    elif gender == 'female':
        #Harris Benedict = 655 + (9.6 * wt) + (1.8 * ht) - (4.7 * age)
        bmr = 10 * wt + 6.25 * ht - 5 * age - 161

    tdee = bmr * act_level

    return round(bmr), round(tdee)

def macro_calc(cal, carb_perc, fat_perc, prot_perc):

    carb = (cal * (carb_perc/100)) / 4
    prot = (cal * (prot_perc/100)) / 4
    fat = (cal * (fat_perc/100)) / 9
    macro = [round(carb), round(prot), round(fat)]

    return macro
