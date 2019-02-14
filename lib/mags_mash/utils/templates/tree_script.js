var margin = {top: 30, right: 20, bottom: 30, left: 20},
    width = 1490,
    barHeight = 30,
    barWidth = (width - margin.left - margin.right) * 0.8;

var i = 0,
    duration = 200,
    root;

var diagonal = d3.linkHorizontal()
    .x(function(d) { return d.y; })
    .y(function(d) { return d.x; });

var tooltip = d3.select("#treeid").append("div").attr("class", 'tooltip').style("pointer-events","none");

var svg = d3.select("#treeid").append("svg")
    .attr("width", width) // + margin.left + margin.right)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


root = d3.hierarchy(tree);
root.x0 = 0;
root.y0 = 0;
update(root)

function update(source) {

    // Compute the flattened node list.
    var nodes = root.descendants();

    var height = Math.max(500, nodes.length * barHeight + margin.top + margin.bottom);

    d3.select("svg").transition()
        .duration(duration)
        .attr("height", height);

    d3.select(self.frameElement).transition()
        .duration(duration)
        .style("height", height + "px");

    // Compute the "layout". TODO https://github.com/d3/d3-hierarchy/issues/67
    var index = -1;
    root.eachBefore(function(n) {
        n.x = ++index * barHeight;
        n.y = n.depth * 20;
    });

    // Update the nodes…
    var node = svg.selectAll(".node")
        .data(nodes, function(d) { return d.id || (d.id = ++i); });

    var nodeEnter = node.enter().append("g")
        .attr("class", "node")
        .attr("transform", function(d) { return "translate(" + source.y0 + "," + source.x0 + ")"; })
        .style("opacity", 0);


    // ========================================================================
    // want to fork here and only include this if its a leaf...
    nodeEnter.append("rect")
        .attr("y", -barHeight/2)
        .attr("height", barHeight)
        .attr("width", leaf_width)
        .attr("border", 0)
        //.style('stroke', "#7ab9ff")
        .style("fill", color)
        .on("click", click)
        .on("mouseover", show_dist_text)
        .on("mousemove", function(d){return tooltip.style("top", (event.pageY - 30) + "px").style("left", event.pageX + "px")})
        .on("mouseout", function(d){return tooltip.style("top", "-9999px").style("opacity","0");})


    nodeEnter.append("text")
        .attr("dy", 5)
        .attr("dx", 4.5)
        .style("font-weight", "bold")
        .text(function(d){
          if(d.children){return ""
          }else{return d.data.dist}
        })

    nodeEnter.append("rect")
        .attr("y", -barHeight / 2)
        .attr("height",barHeight)
        .attr("width", leaf_width)
        .attr("border", 0)
        .attr("transform", leaf_transform)
        //.style('stroke', "#7ab9ff")
        .style("fill", color)
        .on("click", click)
        .on("mouseover",show_compl_text)
        .on("mousemove", function(d){return tooltip.style("top", (event.pageY - 30) + "px").style("left", event.pageX + "px")})
        .on("mouseout", function(d){return tooltip.style("top", "-9999px").style("opacity","0");})

    nodeEnter.append("text")
        .attr("dy", 5)
        .attr("dx", 4.5)
        .style("font-weight", "bold")
        .attr("transform", leaf_transform)
        .text(function(d){
          if(d.children){return ""
          }else{return d.data.compl}
        })
    // ============================================================================
    // ----------------------------------------------------------------------------
    // Enter any new nodes at the parent's previous position.
    nodeEnter.append("rect")
        .attr("y", -barHeight / 2)
        .attr("height", barHeight)
        .attr("transform", leaf_transform_2)
        .attr("width", function(d){
            return barWidth - d.depth * margin.left - leaf_width(d) * 2
        })
        .style("fill", color)
        .on("click", click);
        .on("mouseover", function(d){ if(d.data.dist){return tooltip.text(d.data.name); }})
        .on("mousemove", function(d){ if(d.data.dist){return tooltip.style("top", (event.pageY - 30) + "px").style("left", (event.pageX) + "px")}})
        .on("mouseout", function(d){ if(d.data.dist){return tooltip.style("top", "-9999px"); }});


    nodeEnter.append("text")
        .attr("dy", 5)
        .attr("dx", 5.5)
        .attr('transform', leaf_transform_2)
        .text(function(d) { return d.data.truncated_name; });

    nodeEnter.append("text")
        .attr('dy', 5)
        .attr('dx', function(d){return barWidth - 40 - d.depth * margin.left})
        .style("fill", "#9b9b9b")
        .text(function(d) {return d.data.count})
    // ------------------------------------------------------------------------

    // Transition nodes to their new position.
    nodeEnter.transition()
        .duration(duration)
        .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; })
        .style("opacity", 1);

    node.transition()
        .duration(duration)
        .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; })
        .style("opacity", 1)
        .select("rect")
        .style("fill", color);

    // Transition exiting nodes to the parent's new position.
    node.exit().transition()
        .duration(duration)
        .attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })
        .style("opacity", 0)
        .remove();

    // Stash the old positions for transition.
    root.each(function(d) {
        d.x0 = d.x;
        d.y0 = d.y;
    });
}

function show_compl_text(d){
    return tooltip.style("opacity","1").text("Completeness");
}

function show_dist_text(d){
    return tooltip.style("opacity","1").text("Distance")
}

function leaf_transform(d){
    return "translate("+ (leaf_width(d)).toString() + ",0)"
}

function leaf_transform_2(d){
    return "translate("+ (2 * leaf_width(d)).toString() + ",0)"
}

function leaf_width(d){
    if (d.data.compl){
        return 50
    }else{
        return 0
    }
}

// Toggle children on click.
function click(d) {
    if (d.children) {
        d._children = d.children;
        d.children = null;
    } else {
        d.children = d._children;
        d._children = null;
    }
    update(d);
}

function color(d) {
    return d._children ? "#badaff" : d.children ? "#badaff" : "#7ab9ff";
}