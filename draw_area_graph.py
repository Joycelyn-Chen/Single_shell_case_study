import matplotlib.pyplot as plt

x = range(200, 370, 10)
y = [29311, 22826, 25857, 19924, 20650, 16354, 20434, 16767, 22308, 13182, 11333, 3814, 4033, 4123, 3323, 4374, 8416]
y = [val * ((1000/256) ** 2) for val in y]

plt.plot(x, y, 'bo-')


for xs,ys in zip(x,y):

    label = "{:.2f}".format(ys)

    plt.annotate(label, # this is the text
                 (xs,ys), # these are the coordinates to position the label
                 textcoords="offset points", # how to position the text
                 xytext=(0,10), # distance from text to points (x,y)
                 ha='center') # horizontal alignment can be left, right or center


plt.xlabel('Time Stamp')
plt.ylabel('Area (parsec squared)')
plt.title('Area evolution')
plt.grid(True)
plt.show()
# plt.savefig("area.png")