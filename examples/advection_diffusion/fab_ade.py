import chaospy as cp
import numpy as np
import easyvvuq as uq
import matplotlib.pyplot as plt
import os

# author: Wouter Edeling
__license__ = "LGPL"

#home directory of user
home = os.path.expanduser('~')

#subroutine which runs the EasyVVUQ ensemble with FabSim's campaign2ensemble 
def run_FabUQ_ensemble(campaign_dir, machine = 'localhost'):
    sim_ID = campaign_dir.split('/')[-1]
    os.system("fab " + machine + " run_uq_ensemble:" + sim_ID + ",campaign_dir=" + campaign_dir + ",script_name=ade")

#An EasyVVUQ stochastic collocation advection diffusion example
def test_sc(tmpdir):
    
    # Set up a fresh campaign called "sc"
    my_campaign = uq.Campaign(name='sc', work_dir=tmpdir)

    # Define parameter space
    params = {
        "Pe": {
            "type": "real",
            "min": "1.0",
            "max": "2000.0",
            "default": "100.0"},
        "f": {
            "type": "real",
            "min": "0.0",
            "max": "10.0",
            "default": "1.0"},
        "out_file": {
            "type": "str",
            "default": "output.csv"}}

    output_filename = params["out_file"]["default"]
    output_columns = ["u"]

    # Create an encoder, decoder and collation element 
    encoder = uq.encoders.GenericEncoder(
        template_fname = HOME + '/sc/ade.template',
        delimiter='$',
        target_filename='ade_in.json')
    decoder = uq.decoders.SimpleCSV(target_filename=output_filename,
                                    output_columns=output_columns,
                                    header=0)

    # Create a collation element for this campaign
    collater = uq.collate.AggregateSamples(average=False)
    my_campaign.set_collater(collater)

    # Add the SC app (automatically set as current app)
    my_campaign.add_app(name="sc",
                        params=params,
                        encoder=encoder,
                        decoder=decoder)

    # Create the sampler
    vary = {
        "Pe": cp.Uniform(100.0, 200.0),
        "f": cp.Normal(1.0, 0.1)
    }

    my_sampler = uq.sampling.SCSampler(vary=vary, polynomial_order=1)

    # Associate the sampler with the campaign
    my_campaign.set_sampler(my_sampler)

    # Will draw all (of the finite set of samples)
    my_campaign.draw_samples()
    my_campaign.populate_runs_dir()
 
    #Run execution using Fabsim (on the localhost)
    run_FabUQ_ensemble(my_campaign.campaign_dir)
    
#   Use this instead to run the samples using EasyVVUQ on the localhost
#    my_campaign.apply_for_each_run_dir(uq.actions.ExecuteLocal(
#        "./sc/ade_model.py ade_in.json"))

    my_campaign.collate()

    # Post-processing analysis
    sc_analysis = uq.analysis.SCAnalysis(sampler=my_sampler, qoi_cols=output_columns)

    my_campaign.apply_analysis(sc_analysis)

    results = my_campaign.get_last_analysis()

    # Save and reload campaign
    state_file = tmpdir + "sc_state.json"
    my_campaign.save_state(state_file)
    new = uq.Campaign(state_file=state_file, work_dir=tmpdir)
    print(new)

    return results, sc_analysis

#runs the script
if __name__ == "__main__":

    #home dir of this file    
    HOME = os.path.abspath(os.path.dirname(__file__))

    results, analysis = test_sc("/tmp/")
    mu = results['statistical_moments']['u']['mean']
    std = results['statistical_moments']['u']['std']

    x = np.linspace(0, 1, mu.size)

    ###################################
    # Plot the moments and SC samples #
    ###################################

    fig = plt.figure(figsize=[10, 5])
    ax = fig.add_subplot(121, xlabel='x', ylabel='u',
                         title=r'code mean +/- standard deviation')
    ax.plot(x, mu, 'b', label='mean')
    ax.plot(x, mu + std, '--r', label='std-dev')
    ax.plot(x, mu - std, '--r')

    #####################################
    # Plot the random surrogate samples #
    #####################################

    #for now, only implemented in SC
    if analysis.element_name() == 'SC_Analysis':
        ax = fig.add_subplot(122, xlabel='x', ylabel='u',
                             title='some Monte Carlo surrogate samples')
    
        # generate random samples of unobserved parameter values
        n_mc = 100
        dists = analysis.sampler.vary.vary_dict
        xi_mc = np.zeros([n_mc, 2])
        xi_mc[:, 0] = dists['Pe'].sample(n_mc)
        xi_mc[:, 1] = dists['f'].sample(n_mc)
    
        # evaluate the surrogate at these values
        for i in range(n_mc):
            ax.plot(x, analysis.surrogate('u', xi_mc[i]), 'g')
    
        plt.tight_layout()

    ######################
    # Plot Sobol indices #
    ######################

    fig = plt.figure()
    ax = fig.add_subplot(
        111,
        xlabel='x',
        ylabel='Sobol indices',
        title='spatial dist. Sobol indices, Pe only important in viscous regions')

    lbl = ['Pe', 'f', 'Pe-f interaction']
    idx = 0

    if analysis.element_name() == 'SC_Analysis':
        
        for S_i in results['sobol_indices']['u']:
            ax.plot(x, results['sobol_indices']['u'][S_i], label=lbl[idx])
            idx += 1
    else:
        for S_i in results['sobol_indices']['u'][1]:
            ax.plot(x, results['sobol_indices']['u'][1][S_i], label=lbl[idx])
            idx += 1

    leg = plt.legend(loc=0)
    leg.set_draggable(True)

    plt.tight_layout()

    plt.show()
