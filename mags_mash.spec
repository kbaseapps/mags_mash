/*
A KBase module: mags_mash
*/

module mags_mash {

    typedef structure{
        string workspace_name;
        string ws_ref;
        int n_max_results;
    } mags_mash_params;

    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */
    funcdef run_mags_mash(mags_mash_params params) returns (ReportResults output) authentication required;

};
