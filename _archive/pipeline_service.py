from runner import run_pipeline



def execute_pipeline(

    game,

    platform,

    options,

    destination,

    callback

):


    return run_pipeline(

        game,

        platform,


        extract_user=
            options["extract_user"],


        extract_critic=
            options["extract_critic"],


        process_user=
            options["process_user"],


        process_critic=
            options["process_critic"],


        destination_folder=
            destination,


        progress_callback=
            callback

    )