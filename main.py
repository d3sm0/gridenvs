import sys, time
import gridenvs.examples  # load example gridworld environments
import gym
import numpy as np
import time
from tqdm import tqdm
from agent.agent import KeyboardAgent, AgentOption
from variables import * 
"""
TODO : problem with escape for closing the environment, problem with close().
(Look at the stashed version :
stash@{0}: WIP on branch_options: 3f712e7 some small changes
to change the agent files in order to delete environment in their list of attributes.)
"""

def make_environment_agent(env_name, blurred_bool = False, type_agent = "keyboard_controller", number_gray_colors = NUMBER_GRAY_COLORS, zone_size_x = ZONE_SIZE_X, zone_size_y = ZONE_SIZE_Y):
    env = gym.make(env_name)
    env.reset()
    env.blurred = blurred_bool
    env.number_gray_colors = number_gray_colors
    env.set_zone_size(zone_size_x, zone_size_y)
    agent_position = env.get_hero_position()
    agent_state = (env.get_hero_zone(), 0)
    
    if not hasattr(env.action_space, 'n'):
        raise Exception('Keyboard agent only supports discrete action spaces')

    if type_agent == "keyboard_controller":
        from gridenvs.keyboard_controller import Controls
        agent = KeyboardAgent(env, controls={**Controls.Arrows, **Controls.KeyPad})

    elif type_agent == "agent_option":
        agent = AgentOption(agent_position, agent_state)
    else:
        raise Exception("agent name does not exist")
    return env, agent

def learn_or_play(env, agent, play, iteration = ITERATION_LEARNING):
    """
    0/ The agent chooses an option
    1/ The option makes the action
    TOFIX : I change the info in the env render. Info contains observations for the moment : zone and position of the agent
    2/ The environment gives the feedback
    3/ We update the option's parameters and we get end_option which is True if only if the option is done.
    4/ The agent update his info about the option
    5/ The agent chooses an option and sets its parameter
    """
    initial_agent_position = INITIAL_AGENT_POSITION
    initial_agent_state = INITIAL_AGENT_STATE
    agent.play = play
    if play:
        iteration = 1
        
    for t in tqdm(range(1, iteration + 1)):
        # reset the parameters
        env.reset()
        agent.reset(initial_agent_position, initial_agent_state)
        done = False
        running_option = False
        #start the loop
        while not(done):
            if play:
                time.sleep(1)
                env.render_scaled()
            # if no option acting, choose an option
            if not(running_option): 
                option = agent.choose_option()
                running_option = True
            # else, let the current option act
            action = option.act()
            _, reward, done, info = env.step(action)
            new_position, new_state = info['position'], (info['zone'], info['state_id'])
            end_option = option.update_option(reward, new_position, new_state, action)
            # if the option ended then update the agent's data
            if end_option:
                running_option = False
                agent.update_agent(new_position, new_state, option)
    env.close()
    if not(play):
        return agent

type_agent_list = ["keyboard_controller", "agent_option"]
env_name = 'GE_MazeOptions-v0' if len(sys.argv)<2 else sys.argv[1] #default environment or input from command line 'GE_Montezuma-v1'
type_agent = type_agent_list[1]
env, agent = make_environment_agent(env_name, blurred_bool = False, type_agent = type_agent)
INITIAL_AGENT_POSITION = agent.position
INITIAL_AGENT_STATE = agent.state
agent_learned = learn_or_play(env, agent, iteration = ITERATION_LEARNING, play = False)
learn_or_play(env, agent_learned, play = True)

#play_keyboard(env, agent)
def play_keyboard(env, agent):
    """
    play with the Keyboard agent
    """
    
    #env_blurred, agent_blurred = make_environment_agent(env_name, type_agent = type_agent, blurred_bool = True)
    done = False
    total_reward = 0
    shut_down = agent.human_wants_shut_down
        
    while(not(done) and not(shut_down)):
        shut_down = agent.human_wants_shut_down
        #env_blurred.render_scaled()
        env.render_scaled()
        action = agent.act()
        if action != None:
            _, reward, done, info = env.step(action)
            total_reward += reward
            print('zone = ' + repr(info['zone']))
            #env_blurred.close()
    env.close()
    print('End of the episode')
    print('reward = ' + str(total_reward))
