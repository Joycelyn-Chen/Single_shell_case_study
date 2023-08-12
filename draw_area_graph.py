import matplotlib.pyplot as plt

time = range(200, 370, 10)
area = [29311, 22826, 25857, 19924, 20650, 16354, 20434, 16767, 22308, 13182, 11333, 3814, 4033, 4123, 3323, 4374, 8416]
area = [val * ((1000/256) ** 2) for val in area]
mean_dens = [86.34, 95.85, 89.62, 96.77, 95.35, 92.03, 86.8, 100.08, 90.26, 126.31, 147.23, 125.74, 123.55, 148.08, 96.42, 148.84, 146.8]

# plt.plot(time, area, 'bo-', label="Area")
# plt.plot(time, mean_dens, 'ro-', label="Mean Density")


# for xs,ys in zip(time,area):

#     label = "{:.2f}".format(ys)

#     plt.annotate(label, # this is the text
#                  (xs,ys), # these are the coordinates to position the label
#                  textcoords="offset points", # how to position the text
#                  xytext=(0,10), # distance from text to points (x,y)
#                  ha='center') # horizontal alignment can be left, right or center

# for xs,ys in zip(time,mean_dens):

#     label = "{:.2f}".format(ys)

#     plt.annotate(label, # this is the text
#                  (xs,ys), # these are the coordinates to position the label
#                  textcoords="offset points", # how to position the text
#                  xytext=(0,10), # distance from text to points (x,y)
#                  ha='center') # horizontal alignment can be left, right or center

# plt.xlabel('Time Stamp')
# plt.ylabel('Area (parsec squared)')
# plt.title('Area evolution')
# plt.grid(True)
# plt.legend()
# plt.show()
# plt.savefig("area.png")


fig, ax1 = plt.subplots()

# Plot the first line
ax1.plot(time, area, 'bo-', label='Area', color='blue')
ax1.set_xlabel('Time stamp')
ax1.set_ylabel('Area (parsec squared)', color='black')

# Create the second subplot sharing the same x-axis
ax2 = ax1.twinx()

# Plot the second line
ax2.plot(time, mean_dens, 'ro-', label='Mean Density', color='red')
ax2.set_ylabel('Mean Density', color='black')


for xs,ys in zip(time,area):

    label = "{:.2f}".format(ys)

    ax1.annotate(label, # this is the text
                 (xs,ys), # these are the coordinates to position the label
                 textcoords="offset points", # how to position the text
                 xytext=(0,10), # distance from text to points (x,y)
                 ha='center') # horizontal alignment can be left, right or center

for xs,ys in zip(time,mean_dens):

    label = "{:.2f}".format(ys)

    ax2.annotate(label, # this is the text
                 (xs,ys), # these are the coordinates to position the label
                 textcoords="offset points", # how to position the text
                 xytext=(0,10), # distance from text to points (x,y)
                 ha='center') # horizontal alignment can be left, right or center


# Add legend
lines = ax1.get_lines() + ax2.get_lines()
labels = [line.get_label() for line in lines]
ax1.legend(lines, labels, loc='center left')
plt.show()