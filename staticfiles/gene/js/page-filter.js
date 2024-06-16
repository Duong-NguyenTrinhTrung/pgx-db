$(document).ready(
        $("#id_mean_vep_score").on('change', function() {
            // let table = $('#structures_table').DataTable();
            // table.draw();
            debugger
            let url = "{% url 'gene:filter-gene-detail-page' slug=gene.id %}";
            let mean_vep_score = $("#id_mean_vep_score").val();
            console.log("mean_vep_score: " + mean_vep_score);
            console.log("url: " + url);

            $.get(
                {
                    url: "{% url 'gene:filter-gene-detail-page' slug=gene.id %}",
                }
            )
        }
    )
);
