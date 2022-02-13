from numpy import exp, arange, maximum, minimum, where
from pylab import meshgrid, cm, imshow, contour, clabel, colorbar, axis, title, show


# the function that I'm going to plot
def z_func(num_blocks, num_stacked_boost):
    print(num_blocks)
    print(num_stacked_boost)
    HOOD_THRESHOLD = 10.0

    # What we want: if a hood has 3 stacked boosts, then,
    # if the hood has <10 blocks, the boost should stack as 1+0.5+0.5^2
    # if the hood has >10 blocks,
    mult = HOOD_THRESHOLD / maximum(num_blocks, HOOD_THRESHOLD)
    print(mult)
    spreaded_boost_multiplier = 1000 * num_stacked_boost * mult
    print(spreaded_boost_multiplier)

    for x in range(len(spreaded_boost_multiplier)):
        for y in range(len(spreaded_boost_multiplier[x])):
            if spreaded_boost_multiplier[x][y] >= 3000:
                spreaded_boost_multiplier[x][y] = 1750
            elif spreaded_boost_multiplier[x][y] >= 2000:  # < 3000
                spreaded_boost_multiplier[x][y] = 1500 + (spreaded_boost_multiplier[x][y]-2000)//4
            elif spreaded_boost_multiplier[x][y] > 1000:  # < 2000
                spreaded_boost_multiplier[x][y] = 1000 + (spreaded_boost_multiplier[x][y]-1000)//2
    # spreaded_boost_multiplier = where(spreaded_boost_multiplier >= 3000, 1750, spreaded_boost_multiplier)
    # spreaded_boost_multiplier = where(spreaded_boost_multiplier >= 2500, 1625, spreaded_boost_multiplier)
    # spreaded_boost_multiplier = where(spreaded_boost_multiplier >= 2000, 1500, spreaded_boost_multiplier)
    # spreaded_boost_multiplier = where(spreaded_boost_multiplier >= 1500, 1250, spreaded_boost_multiplier)
    # spreaded_boost_multiplier = where(spreaded_boost_multiplier >= 1000, 1000, spreaded_boost_multiplier)
    print(spreaded_boost_multiplier)
    # if spreaded_boost_multiplier >= 3000:
    #     spreaded_boost_multiplier = 1750

    return spreaded_boost_multiplier


x = arange(0, 101, 1)
y = arange(0, 10, 1)
X, Y = meshgrid(x, y)  # grid of point
Z = z_func(X, Y)  # evaluation of the function on the grid

# im = imshow(Z, cmap=cm.RdBu)  # drawing the function
#im = imshow(Z)  # drawing the function
# adding the Contour lines with labels
#cset = contour(Z, arange(-1, 1.5, 0.2), linewidths=2, cmap=cm.Set2)
#clabel(cset, inline=True, fmt='%1.1f', fontsize=10)
#colorbar(im)  # adding the colobar on the right
# latex fashion title
#show()


from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.gca(projection='3d')
surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1,
                      cmap=cm.RdBu,linewidth=0, antialiased=False)

#ax.zaxis.set_major_locator(LinearLocator(10))
#ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
plt.xlabel("blocks")
plt.ylabel("num_stacked_boosts")

fig.colorbar(surf, shrink=0.5, aspect=5)

plt.show()