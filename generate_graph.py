import json
import matplotlib.pyplot as plt


def counter():
    m = 0
    f = 0
    
    with open('names.json') as json_file:
        data = json.load(json_file)
        for n in data['names']:
            if n['gender'] == 'male':
                m += 1
            else:
                f += 1
    return m, f

if __name__ == "__main__":
    m, f = counter()
    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    labels = 'Male', 'Female'
    sizes = [(m*100/(m+f)),(f*100/(m+f))]

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    #plt.show()
    plt.savefig('graph.png')