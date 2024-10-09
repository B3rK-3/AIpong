import matplotlib.pyplot as plt
from IPython import display

# Turn on interactive mode
plt.ion()

def plot(scores, mean_scores):
    display.clear_output(wait=True)  # Clear previous output in Jupyter Notebook
    plt.clf()  # Clear the current figure
    
    plt.title('Training Progress')
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    
    plt.plot(scores, label='Scores')
    plt.plot(mean_scores, label='Mean Scores')
    
    plt.ylim(ymin=0)  # Set y-axis limit to start from 0
    
    # Annotate last points
    if len(scores) > 0:
        plt.text(len(scores)-1, scores[-1], str(scores[-1]), ha='center', va='bottom')
    if len(mean_scores) > 0:
        plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]), ha='center', va='bottom')
    
    plt.legend()  # Add legend
    display.display(plt.gcf())  # Display the current figure
    plt.pause(0.1)  # Pause to update the plot

# Example usage (only for testing purposes):
# plot([1, 2, 3], [1.5, 1.8, 2.5])
