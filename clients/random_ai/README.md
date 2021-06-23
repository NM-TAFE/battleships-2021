# Battleships AI Client

AI, in this case, stands for Automated Idiot. Thie client basically just shoots at random cells. 

It does keep track of cells that it has already shot at, but nothing more than that. 

It is a great little client to test your own client against. The only thing you need to keep in mind is the format of the attack vector. It should be "a3" or "h10" or "d7", etc. 

With the environment variable `MIRRORED`, you can swap your own grid and the opponent's grid. Place two clients side-by-side and you can see what's happening on the screen.

## Improvements

A simple improvement would be to shoot at cells that are close to any cell that was a hit, preferably the (2, 3, or 4) cells that are directly adjacent to the cell that was hit.
