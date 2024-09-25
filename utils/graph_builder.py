import json, glob, os

def get_asset_image(asset):
  if asset == "gcp":
    return "https://i.imgur.com/I0KiQf3.png"
  elif asset == "aws":
    return "https://i.imgur.com/RHc3fpe.png"
  else:
    return "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Azure_Sphere_logo.svg/1200px-Azure_Sphere_logo.svg.png"

def get_user_image(user_email):
  return "https://i.imgur.com/Mgkh1kz.png"

def get_user_group_image(user_email):
  return "https://i.imgur.com/1NE7jgx.png"

def get_serviceaccount_image(serviceaccount_email):
  return "https://i.imgur.com/Q9ByRTG.png"

def get_tech_profile_icon(profile_name):
  return "https://cdn-icons-png.flaticon.com/512/5741/5741483.png"

def generate_vis_network(output_folder):
    # Create the 'results' folder if it doesn't exist
    results_folder = 'results'
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)
    
    # Get all JSON files in the output folder matching the pattern
    json_files = glob.glob(os.path.join(output_folder, 'gcp_*_data.json'))

    project_names = []

    for json_file in json_files:
        # Extract the project name from the file name
        base_name = os.path.basename(json_file)
        # Assuming file name format is 'gcp_{project_name}_data.json'
        parts = base_name.split('_')
        if len(parts) >= 3:
            # Extract project name by joining all parts except 'gcp' and 'data.json'
            project_name = '_'.join(parts[1:-1])
        else:
            project_name = 'unknown_project'

        project_names.append(project_name)

        # Read the data from the JSON file
        with open(json_file, 'r') as f:
            data = json.load(f)

        # Initialize data structures
        nodes = {}
        edges = []
        mapped_nodes = []

        user_type_keywords = set()
        serviceaccount_type_keywords = set()
        user_filter_keys = {}
        permission_filter_keys = {}
        assets_filter_keys = {}
        assets_filter = []
        assets_permissions = {}

        # Collect data for the table
        table_data = []

        # Process each user in the data
        for user in data:
            user_email = user["email"]
            user_type = user["user_type"]
            module = user.get("module", "unknown_module")  # Asset
            profile_name = user.get("profile", "unknown_profile")
            permissions = user.get("permissions", [])

            # Add user node
            if user_email not in nodes:
                nodes[user_email] = {
                    "id": user_email,
                    "label": user_email,
                    "title": user_email,
                    "shape": "image",
                    "image": get_user_image(user_email) if user_type == "user" else get_serviceaccount_image(user_email),
                    "color": {"background": "grey" if user_type == "serviceAccount" else "yellow"},
                    "font": {"align": "left"}
                }
                if user_type == "user":
                    user_type_keywords.add(user_email)
                else:
                    serviceaccount_type_keywords.add(user_email)

            # Extract user filter keys
            user_roles = [user_email, module, profile_name] + permissions
            user_roles = list(set(user_roles))
            user_filter_keys[user_email] = user_roles

            # Update assets filter keys
            if module not in assets_filter_keys:
                assets_filter_keys[module] = []
            assets_filter_keys[module].extend(user_roles)
            assets_filter_keys[module] = list(set(assets_filter_keys[module]))
            if module not in assets_filter:
                assets_filter.append(module)

            # Add asset node
            asset_node_id = module
            if asset_node_id not in nodes:
                nodes[asset_node_id] = {
                    "id": asset_node_id,
                    "label": asset_node_id,
                    "title": asset_node_id,
                    "shape": "image",
                    "size": 50,
                    "image": get_asset_image(asset_node_id),
                    "color": {"background": "lightblue"}
                }

            # Connect user to asset
            if user_email + "_" + asset_node_id not in mapped_nodes:
                mapped_nodes.append(user_email + "_" + asset_node_id)
                edges.append({"id": user_email + "_" + asset_node_id, "from": user_email, "to": asset_node_id})

            # Add profile node
            profile_node_id = profile_name
            if profile_node_id not in nodes:
                nodes[profile_node_id] = {
                    "id": profile_node_id,
                    "label": profile_node_id,
                    "title": profile_node_id,
                    "shape": "image",
                    "size": 30,
                    "image": get_tech_profile_icon(profile_name),
                    "color": {"background": "lightblue"}
                }
                # Connect asset to profile
                if asset_node_id + "_" + profile_node_id not in mapped_nodes:
                    mapped_nodes.append(asset_node_id + "_" + profile_node_id)
                    edges.append({"id": asset_node_id + "_" + profile_node_id, "from": asset_node_id, "to": profile_node_id})

            # Connect user to profile
            if user_email + "_" + profile_node_id not in mapped_nodes:
                mapped_nodes.append(user_email + "_" + profile_node_id)
                edges.append({"id": user_email + "_" + profile_node_id, "from": user_email, "to": profile_node_id})

            # Iterate through permissions
            for permission in permissions:
                permission_node_id = permission

                if permission_node_id not in permission_filter_keys:
                    permission_filter_keys[permission_node_id] = []

                # Update permission filter keys
                if module not in permission_filter_keys[permission_node_id]:
                    permission_filter_keys[permission_node_id].append(module)
                if profile_node_id not in permission_filter_keys[permission_node_id]:
                    permission_filter_keys[permission_node_id].append(profile_node_id)
                if permission not in permission_filter_keys[permission_node_id]:
                    permission_filter_keys[permission_node_id].append(permission)

                # Add to assets_permissions
                if module not in assets_permissions:
                    assets_permissions[module] = []
                if permission not in assets_permissions[module]:
                    assets_permissions[module].append(permission)

                # Add permission node
                if permission_node_id not in nodes:
                    nodes[permission_node_id] = {
                        "id": permission_node_id,
                        "label": permission_node_id,
                        "title": permission_node_id,
                        "shape": "box",
                        "color": {"background": "pink"}
                    }

                # Connect profile to permission
                if profile_node_id + "_" + permission_node_id not in mapped_nodes:
                    mapped_nodes.append(profile_node_id + "_" + permission_node_id)
                    edges.append({"id": profile_node_id + "_" + permission_node_id, "from": profile_node_id, "to": permission_node_id})
                    permission_filter_keys[permission_node_id].append(profile_node_id)

                # Connect user to permission
                if user_email + "_" + permission_node_id not in mapped_nodes:
                    mapped_nodes.append(user_email + "_" + permission_node_id)
                    edges.append({"id": user_email + "_" + permission_node_id, "from": user_email, "to": permission_node_id})
                    if user_type == "user":
                        user_type_keywords.add(permission_node_id)
                    else:
                        serviceaccount_type_keywords.add(permission_node_id)
                    permission_filter_keys[permission_node_id].append(user_email)

            # Prepare data for the table
            table_entry = {
                "Name": user_email,
                "Type": user_type,
                "Permissions": ", ".join(permissions),
                "Module": module
            }
            table_data.append(table_entry)

        # Generate the HTML code with updated layout and physics settings for the graph
        vis_code = f"""
        <!DOCTYPE html>
        <html lang="en">
          <head>
            <meta charset="UTF-8" />
            <title>Permissions Network | {project_name} </title>
            <!-- Bootstrap CSS -->
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
            <!-- Vis.js -->
            <script type="text/javascript" src="https://visjs.github.io/vis-network/standalone/umd/vis-network.min.js"></script>
            <style type="text/css">
              #mynetwork {{
                width: 100%;
                height: 800px;
                border: 1px solid lightgray;
              }}
            </style>
          </head>
          <body>
            <div class="container-fluid">
              <nav class="navbar navbar-expand-lg navbar-light bg-light">
                <a class="navbar-brand" href="index.html">Permissions Graph</a>
                <div class="collapse navbar-collapse">
                  <ul class="navbar-nav mr-auto">
                    <li class="nav-item">
                      <a class="nav-link" href="index.html">Home</a>
                    </li>
                    <li class="nav-item">
                      <a class="nav-link" href="{project_name}_table.html">Table View</a>
                    </li>
                  </ul>
                </div>
              </nav>
              <h2 class="mt-4">Org Tools Permissions Graph for {project_name}</h2>
              <!-- Filters at the top -->
              <div class="row mt-4">
                <div class="col-md-12">
                  <div class="card">
                    <div class="card-header">
                      <strong>Filters</strong>
                    </div>
                    <div class="card-body">
                      <form class="form-inline">
                        <div class="form-group mb-2">
                          <label for="userTypeFilter" class="mr-2">User Type:</label>
                          <select class="form-control" id="userTypeFilter" onchange="updateNetwork()">
                            <option value="All">All</option>
                            <option value="serviceAccount">Service Account</option>
                            <option value="user">User</option>
                          </select>
                        </div>
                        <div class="form-group mx-sm-3 mb-2">
                          <label for="userFilter" class="mr-2">User:</label>
                          <select class="form-control" id="userFilter" onchange="updateNetwork()">
                            <option value="All">All</option>
                          </select>
                        </div>
                        <div class="form-group mx-sm-3 mb-2">
                          <label for="permissionsFilter" class="mr-2">Permissions:</label>
                          <select class="form-control" id="permissionsFilter" onchange="updateNetwork()">
                            <option value="All">All</option>
                          </select>
                        </div>
                        <div class="form-group mx-sm-3 mb-2">
                          <label for="assetsFilter" class="mr-2">Assets Filter:</label>
                          <select class="form-control" id="assetsFilter" onchange="updateNetwork()">
                            <option value="All">All</option>
                          </select>
                        </div>
                      </form>
                    </div>
                  </div>
                </div>
              </div>
              <!-- Graph occupying full width -->
              <div class="row mt-4">
                <div class="col-md-12">
                  <div id="mynetwork"></div>
                </div>
              </div>
            </div>
            <!-- Bootstrap JS and dependencies -->
            <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js"></script>
            <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
            <script type="text/javascript">
              var nodesArray = {json.dumps(list(nodes.values()))};
              var edgesArray = {json.dumps(edges)};
              var network;
              var user_type_keywords = {json.dumps(list(user_type_keywords))};
              var serviceaccount_type_keywords = {json.dumps(list(serviceaccount_type_keywords))};
              var user_filter_keys = {json.dumps(user_filter_keys)};
              var permission_filter_keys = {json.dumps(permission_filter_keys)};
              var assets_filter_keys = {json.dumps(assets_filter_keys)};
              var assets_permissions = {json.dumps(assets_permissions)};
              var assets_filter = {json.dumps(assets_filter)};
    
              // Create DataSets for nodes and edges
              var nodes = new vis.DataSet(nodesArray);
              var edges = new vis.DataSet(edgesArray);
    
              // Populate user dropdown
              var userFilterDropdown = document.getElementById("userFilter");
              var userData = {json.dumps(list(user_filter_keys.keys()))};
              userData.forEach(function(user) {{
                var option = document.createElement("option");
                option.text = user;
                userFilterDropdown.add(option);
              }});
    
              // Populate permissions dropdown
              var permissionsFilterDropdown = document.getElementById("permissionsFilter");
              var permissionsData = {json.dumps(list(permission_filter_keys.keys()))};
              permissionsData.forEach(function(permission) {{
                var option = document.createElement("option");
                option.text = permission;
                permissionsFilterDropdown.add(option);
              }});
    
              // Populate assets dropdown
              var assetsFilterDropdown = document.getElementById("assetsFilter");
              var assetsData = assets_filter;
              assetsData.forEach(function(asset) {{
                var option = document.createElement("option");
                option.text = asset;
                assetsFilterDropdown.add(option);
              }});
    
              function drawNetwork() {{
                // Create a network
                var container = document.getElementById("mynetwork");
                var data = {{
                  nodes: nodes,
                  edges: edges,
                }};
                var options = {{
                  nodes: {{
                    shape: "dot",
                    scaling: {{
                      min: 20,
                      max: 20,
                    }},
                    font: {{
                      size: 12,
                      align: "left",
                    }},
                  }},
                  edges: {{
                    color: {{ inherit: true }},
                    width: 0.15,
                    smooth: {{
                      type: "continuous",
                    }},
                  }},
                  interaction: {{
                    selectConnectedEdges: true,
                    navigationButtons: true,
                    keyboard: true,
                    tooltipDelay: 10,
                  }},
                  physics: {{
                    forceAtlas2Based: {{
                        gravitationalConstant: -26,
                        centralGravity: 0.005,
                        springLength: 230,
                        springConstant: 0.18,
                    }},
                    maxVelocity: 146,
                    solver: "forceAtlas2Based",
                    timestep: 0.35,
                    stabilization: {{ iterations: 25 }},
                }},
                autoResize: true,
                }};
                network = new vis.Network(container, data, options);
              }}
    
              function updateNetwork() {{
                var userTypeFilter = document.getElementById("userTypeFilter").value;
                var userFilter = document.getElementById("userFilter").value;
                var permissionsFilter = document.getElementById("permissionsFilter").value;
                var assetsFilter = document.getElementById("assetsFilter").value;
                
                // Initialize filteredNodesSet with all node ids
                var filteredNodesSet = new Set(nodes.getIds());
    
                // Filter nodes based on userTypeFilter
                if (userTypeFilter !== "All") {{
                  filteredNodesSet = new Set([...filteredNodesSet].filter(nodeId => {{
                    var node = nodes.get(nodeId);
                    if (!node) return false;
                    if (userTypeFilter === "user" && user_type_keywords.includes(node.label)) {{
                      return true;
                    }} else if (userTypeFilter === "serviceAccount" && serviceaccount_type_keywords.includes(node.label)) {{
                      return true;
                    }} else {{
                      return false;
                    }}
                  }}));
                }}
    
                // Filter nodes based on userFilter
                if (userFilter !== "All") {{
                  var relatedNodes = user_filter_keys[userFilter];
                  filteredNodesSet = new Set([...filteredNodesSet].filter(nodeId => {{
                    var node = nodes.get(nodeId);
                    return node && relatedNodes.includes(node.label);
                  }}));
                }}
    
                // Filter nodes based on permissionsFilter
                if (permissionsFilter !== "All") {{
                  var relatedNodes = permission_filter_keys[permissionsFilter];
                  filteredNodesSet = new Set([...filteredNodesSet].filter(nodeId => {{
                    var node = nodes.get(nodeId);
                    return node && relatedNodes.includes(node.label);
                  }}));
                }}
    
                // Filter nodes based on assetsFilter
                if (assetsFilter !== "All") {{
                  var relatedNodes = assets_filter_keys[assetsFilter];
                  filteredNodesSet = new Set([...filteredNodesSet].filter(nodeId => {{
                    var node = nodes.get(nodeId);
                    return node && relatedNodes.includes(node.label);
                  }}));
                }}
    
                // Update node visibility
                nodes.forEach(function(node) {{
                  if (filteredNodesSet.has(node.id)) {{
                    nodes.update({{ id: node.id, hidden: false }});
                  }} else {{
                    nodes.update({{ id: node.id, hidden: true }});
                  }}
                }});
    
                // Update edge visibility based on connected nodes
                edges.forEach(function(edge) {{
                  if (!nodes.get(edge.from).hidden && !nodes.get(edge.to).hidden) {{
                    edges.update({{ id: edge.id, hidden: false }});
                  }} else {{
                    edges.update({{ id: edge.id, hidden: true }});
                  }}
                }});
              }}
    
              // Initial draw
              drawNetwork();
            </script>
          </body>
        </html>
        """
        # Save the graph HTML file
        graph_file_name = os.path.join(results_folder, f"{project_name}_graph.html")
        with open(graph_file_name, "w") as file:
            file.write(vis_code)

        # Generate the HTML code for the table view
        table_code = f"""
        <!DOCTYPE html>
        <html lang="en">
          <head>
            <meta charset="UTF-8" />
            <title>Permissions Table | {project_name}</title>
            <!-- Bootstrap CSS -->
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
            <!-- DataTables CSS -->
            <link rel="stylesheet" href="https://cdn.datatables.net/1.10.21/css/jquery.dataTables.min.css">
          </head>
          <body>
            <div class="container-fluid">
              <nav class="navbar navbar-expand-lg navbar-light bg-light">
                <a class="navbar-brand" href="index.html">Permissions Table</a>
                <div class="collapse navbar-collapse">
                  <ul class="navbar-nav mr-auto">
                    <li class="nav-item">
                      <a class="nav-link" href="index.html">Home</a>
                    </li>
                    <li class="nav-item">
                      <a class="nav-link" href="{project_name}_graph.html">Graph View</a>
                    </li>
                  </ul>
                </div>
              </nav>
              <h2 class="mt-4">Permissions Table for {project_name}</h2>
              <table id="permissionsTable" class="table table-striped table-bordered" style="width:100%">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Permissions</th>
                    <th>Module</th>
                  </tr>
                </thead>
                <tbody>
        """

        for entry in table_data:
            table_code += f"""
                  <tr>
                    <td>{entry['Name']}</td>
                    <td>{entry['Type']}</td>
                    <td>{entry['Permissions']}</td>
                    <td>{entry['Module']}</td>
                  </tr>
            """

        table_code += """
                </tbody>
              </table>
            </div>
            <!-- jQuery -->
            <script src="https://code.jquery.com/jquery-3.5.1.js"></script>
            <!-- Bootstrap JS -->
            <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
            <!-- DataTables JS -->
            <script src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.min.js"></script>
            <script>
              $(document).ready(function() {
                  $('#permissionsTable').DataTable();
              } );
            </script>
          </body>
        </html>
        """

        # Save the table HTML file
        table_file_name = os.path.join(results_folder, f"{project_name}_table.html")
        with open(table_file_name, "w") as file:
            file.write(table_code)

    # Generate index.html
    index_html = """
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <title>Permissions Projects Index</title>
        <!-- Bootstrap CSS -->
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
      </head>
      <body>
        <div class="container">
          <h2 class="mt-4">Permissions Projects Index</h2>
          <p>Select a project to view its permissions graph or table:</p>
          <ul class="list-group">
    """
    for project_name in project_names:
        index_html += f'''
        <li class="list-group-item">
            <strong>{project_name}</strong>
            <a href="{project_name}_graph.html" class="btn btn-primary btn-sm ml-2">Graph View</a>
            <a href="{project_name}_table.html" class="btn btn-secondary btn-sm ml-2">Table View</a>
        </li>
        '''

    index_html += """
          </ul>
        </div>
        <!-- jQuery -->
        <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
        <!-- Bootstrap JS -->
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
      </body>
    </html>
    """

    # Save index.html in the 'results' folder
    index_file = os.path.join(results_folder, "index.html")
    with open(index_file, "w") as file:
        file.write(index_html)

    print("Graph and table files along with index.html generated in the 'results' folder.")
