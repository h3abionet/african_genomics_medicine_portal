$(document).ready(function () {
  // let db = {
  //     'pharmagkb': [
  //         {
  //             'gene': 'APP',
  //             'uniprot': 'P05067',
  //             'full_name': 'amyloid beta precursor protein',
  //             'protein_class': 'enzyme modulator',
  //             'disease_count': '371',
  //             'dsi': 0.430,
  //             'dpi': 0.862,
  //             'pli': 6.2e02,
  //             'score': 0.900,
  //             'el': 0.200,
  //             'ei': 0.967,
  //             'pmid_count': 1764,
  //             'snp_count': 39,
  //             'first_ref': 1987,
  //             'last_ref': 2018,
  //         },
  //         {},
  //         {},
  //     ],
  //     'gwascatalog': [
  //         {
  //             'gene': {},
  //             'uniprot': {},
  //             'full_name': {},
  //             'protein_class': {},
  //             'disease_count': {},
  //             'dsi': {},
  //             'dpi': {},
  //             'pli': {},
  //             'score': {},
  //             'el': {},
  //             'ei': {},
  //             'pmid_count': {},
  //             'snp_count': {},
  //             'first_ref': {},
  //             'last_ref': {},
  //         },
  //         {},
  //         {},
  //     ]
  // };

  // populate the data table with data object (db)
  function populateDataTable(dataObject) {
    console.log("populating data table...");
    // clear the table before populating it with more data
    $("#detail-table").DataTable().clear();

    var length = Object.keys(dataObject.pharmgkb).length;
    for (var i = 1; i < length + 1; i++) {
      var customer = dataObject.customers['customer' + i];

      // You could also use an ajax property on the data table initialization
      $('#example').dataTable().fnAddData([
        customer.first_name,
        customer.last_name,
        customer.occupation,
        customer.email_address
      ]);
    }
  }

  populateDataTable(db);
});
