$(document).ready(function () {
  // initialize data table for detail items
  $('#detail-table, #snps-drugs, #star-alleles-drugs, #snp-diseases').DataTable({
    dom: 'Bfrtip',
    buttons: [
      'copy', 'csv', 'excel', 'print'
    ]    
  });
});