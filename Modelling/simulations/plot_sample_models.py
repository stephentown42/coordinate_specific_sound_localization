"""

Figure 5A - Demonstration of the influence of each parameter on 
model output


"""

import os, sys

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.abspath( os.path.join(os.path.dirname(__file__), '../..')))
from Modelling import cf_simulate as csim
from Analysis import cf_plot as cfp

plt.style.use('seaborn')


def stem_plot(ax, x, y, color):

    # ax.plot([x, x], [0, y], c=color)
    ax.plot(x, y, marker='o', c=color, markersize=3)

    return None


class model:
    """
    horizontal offset is given in degrees
    vert_offset typically in range of 1 to 2
    amplitude typically in range of 0 to 1 
    coolness = inverse temperature (typically > 2)
    """

    def __init__(self, vert_offset, horiz_offset, amplitude, coolness):
        """
        Conversion to float may not be strictly necessary but just to ensure against type errors
        """

        self.theta = np.arange(-180, 180, 1)
        self.coefs = dict(
            vert_offset = float(vert_offset),
            horiz_offset = float(horiz_offset),
            amplitude = float(amplitude),
            coolness = float(coolness)
        )

        self.z = csim.run_mdl(self.theta, self.coefs)   # Action 1: e.g. go west or left
        self.alt_z = 1 - self.z                         # Action 2: e.g. go east or right

        self.p = []
        for z in zip(self.z, self.alt_z):
            self.p.append(csim.softmax(z, beta=coolness))



    def plot(self, ax, action=0,  color='k', fill=True):
        
        if action == 0:
            ax.plot( self.theta, self.z, c=color, lw=1.25)
        elif action == 1:
            ax.plot( self.theta, self.alt_z, c=color, lw=1.25)        
        
        if fill:
            
            x = (self.coefs['horiz_offset'] / np.pi) * 180          
            y = self.coefs['vert_offset']
            
            ax.plot([-180, 180], [y, y], c=color, ls='--', lw=0.75)         # Line at parameter value
            ax.plot([x, x], [0, 1], c=color, ls='--', lw=0.75)              # Line at parameter value
            
            
            ax.fill_between(self.theta, self.z, np.full_like(self.z, y), color=color, alpha=0.3)    # Patch fill 

        return None
        

    def polar_plot(self, ax, color):
            
            # Plot action 1
            phi = (self.theta / 180) * np.pi
            x = np.cos(phi) * self.z
            y = np.sin(phi) * self.z

            ax.plot( x, y, c=color)
        
            # # Plot action 2
            # x = np.cos(self.theta) * self.alt_z
            # y = np.sin(self.theta) * self.alt_z

            # ax.plot( x, y, c=color)        
        
            ax.set_xlim([-1, 1])
            ax.set_ylim([-1, 1])

            # if fill:
                
            #     x = (self.coefs['horiz_offset'] / np.pi) * 180          
            #     y = self.coefs['vert_offset']
                
            #     ax.plot([-180, 180], [y, y], c=color, ls='--', lw=1)         # Line at parameter value
            #     ax.plot([x, x], [0, 1], c=color, ls='--', lw=1)         # Line at parameter value
                
            #     ax.fill_between(self.theta, self.z, np.full_like(self.z, y), color=color, alpha=0.3)    # Patch fill 

            return None
            



    def plot_response_prob(self, ax, color_0, color_1):

        p = np.transpose(self.p)

        ax.plot( [-180, 180], [0.5, 0.5], c='#888888', lw=1.25, ls='--')
        ax.plot( self.theta, p[0], c=color_0, lw=1.25)


        # for (theta, p) in zip(self.theta, self.p):
        #     if theta % 30 == 0:
                
        #         if p[0] > p[1]:
        #             stem_plot(ax, theta, p[0], color_0)
        #             stem_plot(ax, theta, p[1], color_1)
        #         else:
        #             stem_plot(ax, theta, p[1], color_1)
        #             stem_plot(ax, theta, p[0], color_0)

        ax.set_ylim((0, 1))
                    

def format_xticks(ax, label=True, xlim=180):

    ax.set_xticks([-180, -90, 0, 90, 180])
    ax.set_xlim([-xlim, xlim])

    if label:
        ax.set_xticklabels(['-180', '', '0', '', '180'], rotation=45, fontsize=7)            
        ax.set_xlabel(r'$\theta  (°)$', fontsize=8)
    else:
        ax.set_xticklabels('')

    return None


def format_yticks(ax, label=None):

    ax.set_yticks([0, 0.25, 0.5, 0.75, 1])  
    ax.set_yticklabels(['0', '', '0.5', '', '1'], fontsize=7)            

    if label is not None:
        ax.set_ylabel(label, rotation=0, fontsize=8, fontweight='bold')

    return None





def main():
        
    # Define models
    itchy = model(0.6, -60, 0.5, 3)    
    scratchy = model(0.7, 90, 0.25, 3)
    poochy = model(0.6, 0, 0.4, 0.5)        # Same sinusoid as itchy but lower inverse temperature


    fig_size = (6,3)
    fig = plt.figure(figsize=fig_size)       

    axs = dict(
        itchy     = fig.add_axes( cfp.cm2norm([1, 2, 2, 1.5], fig_size)),       # Parameter comparison
        scratchy  = fig.add_axes( cfp.cm2norm([1, 4.5, 2, 1.5], fig_size)),       # Parameter comparison
        actions   = fig.add_axes( cfp.cm2norm([6.5, 3.3, 2, 1.5], fig_size)),         # Response 1 vs 2: Activation
        low_temp  = fig.add_axes( cfp.cm2norm([11, 4.5, 2, 1.5], fig_size)),         # Response probability: Low Inverse Temperature
        high_temp = fig.add_axes( cfp.cm2norm([11, 2, 2, 1.5], fig_size)),         # Response probability: High Inverse Temperature        
    )  

    colors = dict(
        act1 = 'g',
        act2 = '#808000'
    )

    # Compare models with different parameters   
    scratchy.plot(axs['scratchy'])
    format_xticks(axs['scratchy'], label=False)
    format_yticks(axs['scratchy'], label=None)

    axs['scratchy'].text(280, 0.85, r'$\beta_0 = 0.7$', fontsize=7, color='.1')
    axs['scratchy'].text(220, 0.7, r'$\beta_1 = 0.25$', fontsize=7, color='.1', rotation=90)
    axs['scratchy'].text(280, 0.1, r'$\beta_2 = 90°$', fontsize=7, color='.1')
    axs['scratchy'].text(0, 1.6, r'$z = \beta_0 + \beta_1 cos(\theta - \beta_2)$', fontsize=8, ha='center', va='center', color='.1')  # z = 𝛽0 + 𝛽1cos(𝜃HEAD - 𝛽2) 
    
    itchy.plot(axs['itchy'], action=0, color=colors['act1'])   
    format_xticks(axs['itchy'], label=True)
    format_yticks(axs['itchy'], label='z')

    axs['itchy'].text(280, 0.7, r'$\beta_0 = 0.6$', fontsize=7, color=colors['act1'])
    axs['itchy'].text(220, 0.6, r'$\beta_1 = 0.4$', fontsize=7, color=colors['act1'], rotation=90)
    axs['itchy'].text(280, 0.075, r'$\beta_2 = -60°$', fontsize=7, color=colors['act1'])

    # Show the activation functions for two different actions
    ax = axs['actions']
    
    itchy.plot(ax, action=0, color=colors['act1'], fill=False)
    itchy.plot(ax, action=1, color=colors['act2'], fill=False) 

    ax.text(0, -1.2, r'$z_{Left} = 0.6 + 0.4 cos(\theta + 60)$', fontsize=8, ha='center', va='center', color=colors['act1'])  # z = 𝛽0 + 𝛽1cos(𝜃HEAD - 𝛽2) 
    ax.text(0, -1.5, r'$z_{Right} = 1 - z_{Left}$', fontsize=8, ha='center', va='center', color=colors['act2'], fontweight='bold')  # z = 𝛽0 + 𝛽1cos(𝜃HEAD - 𝛽2) 
    
    ax.text(-130, 1.2, 'Go Left', fontsize=8, ha='center', color=colors['act1'])    
    ax.text(130, 1.2, 'Go Right', fontsize=8, ha='center', color=colors['act2'])  
    
    
    format_xticks(ax, label=True)
    format_yticks(ax, label='z')

    # Compare the effects of using a high or low temperature 
    itchy.plot_response_prob(axs['high_temp'], colors['act1'], colors['act2'])
    poochy.plot_response_prob(axs['low_temp'], colors['act1'], colors['act2'])

    axs['low_temp'].text(210, 0.5, r'$\beta_{inv. temp} = 0.5$', fontsize=7, ha='left', color=colors['act1'])
    axs['high_temp'].text(210, 0.5, r'$\beta_{inv. temp} = 3$',  fontsize=7, ha='left', color=colors['act1'])

    format_xticks(axs['high_temp'], label=True, xlim=200)
    format_yticks(axs['high_temp'], label='None')
    axs['high_temp'].set_ylabel('Response Prob.', fontsize=8, rotation=90)

    format_xticks(axs['low_temp'], label=False, xlim=200)
    format_yticks(axs['low_temp'], label=None)

    # plt.show()
    plt.savefig('Modelling/images/Demo_models.png', dpi=300)
    plt.close()




if __name__ == '__main__':
    main()