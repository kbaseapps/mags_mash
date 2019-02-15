var margin = {top: 30, right: 20, bottom: 30, left: 20},
    barHeight = 25,
    map_width = (sources.length + 1) * barHeight,
    map_window_width = Math.min(map_width, 600),
    tree_map_gap = 20,
    title_height = 150,
    lwidth = 40;

var min_tree_width = 300;

var allotted_width = Math.max(map_window_width + min_tree_width + tree_map_gap + margin.left + margin.right,850);

var tree_width = Math.max(allotted_width - (map_window_width + tree_map_gap + margin.left + margin.right), min_tree_width);
var barWidth = tree_width;
    // barWidth = (tree_width - margin.left - margin.right) * 0.8;

var i = 0,
    duration = 200,
    root;

var diagonal = d3.linkHorizontal()
    .x(function(d) { return d.y; })
    .y(function(d) { return d.x; });

var tooltip = d3.select("#treeid").append("div").attr("class", 'tooltip').style("pointer-events","none");

var svg = d3.select("#treeid").append("svg")
    .attr("width", tree_width + tree_map_gap)// + margin.left + margin.right)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var mapsvg = d3.select("#treemap").style("width",map_width).append("svg")
    .attr("width", map_width + tree_map_gap)
    .attr("height", "100%")
    .append("g")
    .attr("transform", "translate(0," + margin.top + ")");

var svg2 = d3.select("#treelegend").style("width", allotted_width).append("svg")
    .attr("width", allotted_width)
  .append("g")
    .attr("transform", "translate(" + (margin.left + tree_map_gap + tree_width) + "," + margin.top + ")");

var domainList = [0]
for (i = 0; i<9; i++){
  domainList.push((number_of_points/8) * i)
}

for (i = 0; i < sources.length; i++){
  var titles = mapsvg.append('rect')
     .attr("y", 0)
     .attr("x", (i * barHeight) + tree_map_gap)
     .attr("height", title_height)
     .attr("width", barHeight)
     .attr("fill" , '#7ab9ff')
     .attr("stroke", "#3182bd")
     // .attr("stroke", "white")

  mapsvg.append("text")
     .style("font-weight", "bold")
     .attr("transform", "translate("+((i * barHeight) + tree_map_gap + (barHeight/4))+","+(-(i * barHeight) - barWidth - tree_map_gap +(title_height/2) )+") rotate(90)")
     // .attr("transform", "translate("+ (barHeight/2) +","+ (title_height/2) +") " + "rotate(90)")
     .style("fill", "black")
     .style("text-anchor", "middle")
     .attr("y", 0)
     .attr("x", (i * barHeight) + barWidth + tree_map_gap)
     .text(sources[i]);
     // .text(sources[i]);
}

var colorScale = d3.scaleLinear()
    .domain(domainList)
    .range(["#2c7bb6","#00a6ca","#00ccbc","#90eb9d","#ffff8c","#f9d057","#f29e2e","#e76818","#d7191c"]);



var countScale = d3.scaleLinear()
  .domain([0, number_of_points])
  .range([0, allotted_width])

//Calculate the variables for the temp gradient
var numStops = 10;
countRange = countScale.domain();
countRange[2] = countRange[1] - countRange[0];
countPoint = [];
for(var i = 0; i < numStops; i++) {
  countPoint.push(i * countRange[2]/(numStops-1) + countRange[0]);
}

var defs = mapsvg.append("defs");

var linearGradient = defs.append("linearGradient")
    .attr("id", "linear-gradient")
    .attr("x1", "0%").attr("y1", "0%")
    .attr("x2", "100%").attr("y2", "0%")
    .selectAll("stop")
    .data( d3.range(numStops) )
    .enter().append("stop")
    .attr("offset", function(d,i) { 
      return countScale( countPoint[i] )/allotted_width;
    })   
    .attr("stop-color", function(d,i) { 
      return colorScale( countPoint[i] ); 
    });
 
// //Append multiple color stops by using D3's data/enter step
// linearGradient.selectAll("stop")
//     .data( colorScale.range() )
//     .enter().append("stop")
//     .attr("offset", function(d,i) { return i/(colorScale.range().length-1); })
//     .attr("stop-color", function(d) { return d; });

var legendY_pos = -45
var legendWidth = 220;
var legendHeight = 15
var legendsvg = svg2.append('g')
    .attr("class","legendWrapper")
    .attr("transform","translate("+ (map_window_width/2) +","+ (40) +")")

legendsvg.append("rect")
    .attr("x", -legendWidth/2)
    .attr("y", legendY_pos)
    .attr("width", legendWidth)
    .attr("height", legendHeight)
    .style("fill", "url(#linear-gradient)")

legendsvg.append("text")
    .attr("class","legendTitle")
    .attr("x",0)
    .attr("y",legendY_pos-10)
    .style("text-anchor","middle")
    .text("Number of Studies")

//Set scale for x-axis
var xScale = d3.scaleLinear()
   .range([-legendWidth/2, legendWidth/2])
   .domain([ 0, number_of_points] );

//Define x-axis
var xAxis = d3.axisBottom()
    .ticks(5)
    //.tickFormat(formatPercent)
    .scale(xScale);

//Set up X axis
legendsvg.append("g")
  .attr("class", "axis")
  .attr("transform", "translate(0," + (legendY_pos + legendHeight) + ")")
  .call(xAxis);

root = d3.hierarchy(tree);
root.x0 = 0;
root.y0 = 0;
update_tree(root)



function update_tree(source) {

  // Compute the flattened node list.
  var nodes = root.descendants();

  var height = Math.max(50, (nodes.length * barHeight) + margin.top + margin.bottom + title_height);

  // d3.select("svg2").transition()
  //     .duration(duration)
  //     .attr("height",height)

  d3.select("svg").transition()
      .duration(duration)
      .attr("height", height);

  // d3.select(self.frameElement).transition()
  //     .duration(duration)
  //     .style("height", height + "px");

  d3.select("mapsvg").transition()
    .duration(duration)
    .attr("height", height);

  d3.select(self.frameElement).transition()
    .duration(duration)
    .style("height", height + "px")

  // Compute the "layout". TODO https://github.com/d3/d3-hierarchy/issues/67
  var index = -1;
  root.eachBefore(function(n) {
    n.x = ++index * barHeight;
    n.y = n.depth * 20;
  });

  // update nodes for map
  // var map_node = svg2.selectAll(".node")
  //   .data(nodes, function(d) { return d.id || (d.id = ++i); });

  // Update the nodes…
  var node = svg.selectAll(".node")
    .data(nodes, function(d) { return d.id || (d.id = ++i); });

  var nodeEnter = node.enter().append("g")
      .attr("class", "node")
      .attr("transform", function(d) { return "translate(" + source.y0 + "," + source.x0 + ")"; })
      .style("opacity", 0);

  var map_node = mapsvg.selectAll(".node")
    .data(nodes, function(d) {return d.id || (d.id = ++i);});

  var map_nodeEnter = map_node.enter().append("g")
      .attr("class", "node")
      .attr("transform", function(d) { return "translate(0," + source.x0 + ")"; })
      .style("opacity", 0);

  // var map_nodeEnter = map_node.enter().append("g")
  //     .attr("class", "node")
  //     .attr("transform", function(d) { return "translate(" + source.y0 + "," + source.x0 + ")"; })
  //     .style("opacity", 0);

  // ========================================================================
  // do the heat map thing here.
  for (i = 0; i < sources.length; i++){
    map_nodeEnter.append("rect")
        .attr("y", (-barHeight/2) + title_height + tree_map_gap)
        .attr("height", barHeight)
        .attr("width", barHeight)
        .attr("transform", function(d) {return "translate("+((i * barHeight) + tree_map_gap)+",0)"})
        .attr("border", 0)
        .style("stroke","white")
        .style("stroke-opacity", 0.6)
        //.style("fill", "#f8d9039")
        .style("fill", function(d) {return colorScale(d.data.sources[i])})
  }
    
  // ========================================================================
  // want to fork here and only include this if its a leaf...
  nodeEnter.append("rect")
      .attr("class", "tree_rect")
      .attr("y", (-barHeight/2) + title_height + tree_map_gap)
      .attr("height", barHeight)
      .attr("width", leaf_width)
      .attr("border", 0)
      //.style('stroke', "#7ab9ff")
      .style("fill", color)
      .on("click", click)
      // .append("svg:title")
      // .text("Distance")
      .on("mouseover", show_dist_text)
      .on("mousemove", function(d){ return tooltip.style("top", (event.pageY - 30) + "px").style("left", (event.pageX) + "px")})
      .on("mouseout", function(d){return tooltip.style("top", "-9999px");})

  nodeEnter.append("text")
        .attr('y', title_height + tree_map_gap)
        .attr("dy", 5)
        .attr("dx", 4.5)
        .style("font-weight", "bold")
        .text(function(d){
          if(d.children){return ""
          }else{return d.data.dist}
        })

  nodeEnter.append("rect")
        .attr("class", "tree_rect")
        .attr("y", (-barHeight / 2) + title_height + tree_map_gap)
        .attr("height",barHeight)
        .attr("width", leaf_width)
        .attr("border", 0)
        .attr("transform", leaf_transform)
        //.style('stroke', "#7ab9ff")
        .style("fill", color)
        .on("click", click)
        // .append("svg:title")
        // .text("Distance")
        .on("mouseover",show_compl_text)
        .on("mousemove", function(d){ return tooltip.style("top", (event.pageY - 30) + "px").style("left", (event.pageX) + "px")})
        .on("mouseout", function(d){return tooltip.style("top", "-9999px");})

  nodeEnter.append("text")
        .attr('y', title_height + tree_map_gap)
        .attr("dy", 5)
        .attr("dx", 4.5)
        .style("font-weight", "bold")
        .attr("transform", leaf_transform)
        .text(function(d){
          if(d.children){return ""
          }else{return d.data.compl}
        })
  // ========================================================================
  // ------------------------------------------------------------------------
  // Enter any new nodes at the parent's previous position.
  nodeEnter.append("rect")
      .attr("class", "tree_rect")
      .attr("y", (-barHeight / 2) + title_height + tree_map_gap)
      .attr("height", barHeight)
      .attr("transform", leaf_transform_2)
      .attr("width", function(d){
          return barWidth - d.depth * margin.left - leaf_width(d) * 2
      })
      .style("fill", color)
      .on("click", click)
      .on("mouseover", function(d){ if(d.data.dist){return tooltip.text(d.data.name); }})
      .on("mousemove", function(d){ if(d.data.dist){return tooltip.style("top", (event.pageY - 30) + "px").style("left", (event.pageX) + "px")}})
      .on("mouseout", function(d){ if(d.data.dist){return tooltip.style("top", "-9999px"); }});


  nodeEnter.append("text")
      .attr('y', title_height + tree_map_gap)
      .attr("dy", 5)
      .attr("dx", 5.5)
      .attr('transform', leaf_transform_2)
      .text(function(d) { return d.data.truncated_name; })

  nodeEnter.append("text")
      .attr('y', title_height + tree_map_gap)
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

  map_nodeEnter.transition()
      .duration(duration)
      .attr("transform", function(d) { return "translate(0," + d.x + ")"; })
      .style("opacity", 1);


  node.transition()
      .duration(duration)
      .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; })
      .style("opacity", 1)
    .select("g.tree_rect")
      .style("fill", color);

  map_node.transition()
      .attr("transform", function(d) { return "translate(0," + d.x + ")"; })
      .style("opacity", 1)
    .select("g.tree_rect")
      .style("fill", color);
 
  // Transition exiting nodes to the parent's new position.
  node.exit().transition()
      .duration(duration)
      .attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })
      .style("opacity", 0)
      .remove();

  map_node.exit().transition()
      .duration(duration)
      // .attr("transform", function(d) { return "translate(0," + source.x + ")"; })
      .style("opacity", 0)
      .remove();

  // Stash the old positions for transition.
  root.each(function(d) {
    d.x0 = d.x;
    d.y0 = d.y;
  });

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
  update_tree(d);
}

function show_compl_text(d){
  return tooltip.text("Completeness");
}

function show_dist_text(d){
  return tooltip.text("Distance")
}

function leaf_transform(d){
  return "translate("+ (leaf_width(d)).toString() + ",0)"
}

function leaf_transform_2(d){
  return "translate("+ (2 * leaf_width(d)).toString() + ",0)"
}

function leaf_width(d){
  if (d.data.compl){
    return lwidth
  }else{
    return 0
  }
}

// function stroke_color(d){
//   return d._children ? "#3182bd" : d.children ? "#3182bd" : "#7ab9ff";
// }

function color(d) {
  return d._children ? "#badaff" : d.children ? "#badaff" : "#7ab9ff";
}