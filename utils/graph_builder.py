import json

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

def generate_vis_network(data):
    nodes = {}
    edges = []

    user_type_keywords = set()
    serviceaccount_type_keywords = set()
    user_filter_keys = {}
    permission_filter_keys = {}
    assets_filter_keys = {}
    assets_filter = []
    assets_permissions = {}

    # Create nodes and edges based on JSON data
    mapped_nodes = []
    for user in data:
        user_email = user["email"]
        user_type = user["user_type"]

        # Add user node
        if user_email not in nodes:
            nodes[user_email] = {
              "id": user_email, 
              "label": user_email, 
              "title": user_email, 
              "shape": "image",
              "image": get_user_image(user_email) if user_type == "user" else get_user_group_image(user_email) if user_type == "group" else get_serviceaccount_image(user_email),
              "color": {"background": "grey" if user_type == "serviceAccount" else "yellow"}, 
              "font": {"align": "left"}
            }
            user_type_keywords.add(user_email) if user_type == "user" or user_type == "group" else serviceaccount_type_keywords.add(user_email)

        # Extract user filter keys
        user_roles = []
        ## append email to user_roles
        user_roles.append(user_email)
        for asset, profiles in user["assets"].items():
            for profile_name, permissions in profiles.items():
                ## also append asset name 
                user_roles.extend([asset, profile_name, *permissions])
                user_type_keywords.add(profile_name) if user_type == "user" or user_type == "group" else serviceaccount_type_keywords.add(profile_name)
            user_roles = list(set(user_roles))
            user_filter_keys[user_email] = user_roles
            if asset not in assets_filter_keys:
              assets_filter_keys[asset] = []
            assets_filter_keys[asset].extend(list(set(user_roles)))
            assets_filter_keys[asset].append(asset)
            assets_filter_keys[asset].extend(list(set(profiles.keys())))
            assets_filter_keys[asset] = list(set(assets_filter_keys[asset]))
            assets_filter.append(asset)
            
        # Iterate through assets (e.g., "gcp") for the user
        for asset, roles in user["assets"].items():
            asset_node_id = asset
            user_type_keywords.add(asset_node_id) if user_type == "user" or user_type == "group" else serviceaccount_type_keywords.add(asset_node_id)
            # Add asset node
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
                if user_email+"_"+asset_node_id not in mapped_nodes:
                  mapped_nodes.append(user_email+"_"+asset_node_id)
                edges.append({"from": user_email, "to": asset_node_id})

            # Iterate through roles for each asset
            for profile_name, permissions in roles.items():
                profile_node_id = f"{profile_name}"
                """
                if profile_name+"_"+asset not in mapped_nodes:
                    mapped_nodes.append(profile_name+"_"+asset)
                    edges.append({"from": asset_node_id, "to": profile_name})
                """

                # Add profile node
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
                    if asset_node_id+"_"+profile_node_id not in mapped_nodes:
                      mapped_nodes.append(asset_node_id+"_"+profile_node_id)
                      edges.append({"from": asset_node_id, "to": profile_node_id})
                    
                    # Connect user to profile
                    if user_email+"_"+profile_node_id not in mapped_nodes:
                      mapped_nodes.append(user_email+"_"+profile_node_id)
                      edges.append({"from": user_email, "to": profile_node_id})

                # Iterate through permissions for each role
                for permission in permissions:
                    permission_node_id = f"{permission}"

                    if permission_node_id not in permission_filter_keys:
                      permission_filter_keys[permission_node_id] = []

                    ## Let's add asset, profile name, and that permission in the permission filter keys and only add if its not in that key's list
                    if asset_node_id not in permission_filter_keys[permission_node_id]:
                      permission_filter_keys[permission_node_id].append(asset_node_id)
                    if profile_node_id not in permission_filter_keys[permission_node_id]:
                      permission_filter_keys[permission_node_id].append(profile_node_id)
                    if permission not in permission_filter_keys[permission_node_id]:
                      permission_filter_keys[permission_node_id].append(permission)

                    ## Add permission to assets_permissions for dynamic dropdown
                    if asset not in assets_permissions:
                      assets_permissions[asset] = []
                    if permission not in assets_permissions[asset]:
                      assets_permissions[asset].append(permission)
                    # Add permission node
                    if permission_node_id not in nodes:
                      nodes[permission_node_id] = {"id": permission_node_id, "label": permission_node_id, "title": permission_node_id, "shape": "box", "color": {"background": "pink"}}
                    
                    # Connect profile to permission
                    if profile_node_id+"_"+permission_node_id not in mapped_nodes:
                      mapped_nodes.append(profile_node_id+"_"+permission_node_id)
                      edges.append({"from": profile_node_id, "to": permission_node_id})
                      permission_filter_keys[permission_node_id].append(profile_node_id)

                    # Connect user to permission
                    if user_email+"_"+permission_node_id not in mapped_nodes:
                      edges.append({"from": user_email, "to": permission_node_id})
                      user_type_keywords.add(permission_node_id) if user_type == "user" or user_type == "group" else serviceaccount_type_keywords.add(permission_node_id)
                      mapped_nodes.append(user_email+"_"+permission_node_id)
                      permission_filter_keys[permission_node_id].append(user_email)

    # Create JavaScript code for vis network
    vis_code = f"""
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta http-equiv="content-type" content="text/html; charset=UTF8" />
        <title>Permissions Network | Xposed </title>
        <script type="text/javascript" src="https://visjs.github.io/vis-network/standalone/umd/vis-network.min.js"></script>
        <style type="text/css">
          #mynetwork {{
            width: 100%;
            height: 800px;
          }}
        </style>
      </head>
      <body>
        <h2>Org Tools Permissions Graph</h2>
        
        <label for="userTypeFilter">User Type:</label>
        <select id="userTypeFilter" onchange="updateNetwork()">
          <option value="All">All</option>
          <option value="serviceAccount">Service Account</option>
          <option value="user">User</option>
        </select>

        <label for="userFilter">User:</label>
        <select id="userFilter" onchange="updateNetwork()">
          <option value="All">All</option>
          <!-- Add options dynamically using JavaScript -->
        </select>

        <label for="permissionsFilter">Permissions:</label>
        <select id="permissionsFilter" onchange="updateNetwork()">
          <option value="All">All</option>
          <!-- Add options dynamically using JavaScript -->
        </select>

        <label for="assetsFilter">Assets Filter:</label>
        <select id="assetsFilter" onchange="updateNetwork()">
          <option value="All">All</option>
          <!-- Add options dynamically using JavaScript -->
        </select>
        
        <div id="mynetwork"></div>
        
        <script type="text/javascript">
          var nodes = {json.dumps(list(nodes.values()))};
          var edges = {json.dumps(edges)};
          var network;
          var user_type_keywords = {json.dumps(list(user_type_keywords))};
          var serviceaccount_type_keywords = {json.dumps(list(serviceaccount_type_keywords))};
          var user_filter_keys = {json.dumps(user_filter_keys)};
          var permission_filter_keys = {json.dumps(permission_filter_keys)};
          var assets_filter_keys = {json.dumps(assets_filter_keys)};
          var assets_permissions = {json.dumps(assets_permissions)};

          // Extract user, user email, and permissions data for dropdowns
          var userData = {json.dumps(list(user_filter_keys.keys()))};
          var assetsData = {json.dumps(list(assets_filter_keys.keys()))};

          // Populate user, user email, and permissions dropdowns
          var userFilterDropdown = document.getElementById("userFilter");
          var permissionsFilterDropdown = document.getElementById("permissionsFilter");

          userData.forEach(function(user) {{
            var option = document.createElement("option");
            option.text = user;
            userFilterDropdown.add(option);
          }});

          // create group of option and it name should be key from assets_permissions and value should be the key's value
          for (var key in assets_permissions) {{
            // Create an optgroup element for each key
            var optgroup = document.createElement("optgroup");
            optgroup.label = key;
            // Iterate through the values for each key
            for (var i = 0; i < assets_permissions[key].length; i++) {{
              var option = document.createElement("option");
              option.text = assets_permissions[key][i];
              optgroup.appendChild(option);
            }}
            permissionsFilterDropdown.add(optgroup);
          }}

          // Populate assets dropdown
          var assetsFilterDropdown = document.getElementById("assetsFilter");
          assetsData.forEach(function(asset) {{
            var option = document.createElement("option");
            option.text = asset;
            assetsFilterDropdown.add(option);
          }});
          
          function redrawAll() {{
            // remove positions
            for (var i = 0; i < nodes.length; i++) {{
              delete nodes[i].x;
              delete nodes[i].y;
            }}

            // create a network
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
                    hideNodesOnDrag: true,
                    hideEdgesOnZoom: true,
                    navigationButtons: true,
                    keyboard: true,
                    tooltipDelay: 10,
                }},
                layout: {{
                    improvedLayout: true,
                    clusterThreshold: 150,
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
                height: "800px",
            }};
            network = new vis.Network(container, data, options);
          }}

          function updateNetwork() {{
            var userTypeFilter = document.getElementById("userTypeFilter").value;
            var userFilter = document.getElementById("userFilter").value;
            var permissionsFilter = document.getElementById("permissionsFilter").value;
            var assetsFilter = document.getElementById("assetsFilter").value;
            
            // Apply filters and update nodes and edges
            // Implement your logic here based on the selected filters

            // Example: You can filter nodes based on user type
            var filteredNodes = nodes.filter(function(node) {{
              return (
                (userTypeFilter === "All" || 
                 (userTypeFilter === "serviceAccount" && serviceaccount_type_keywords.includes(node.label)) ||
                 (userTypeFilter === "user" && user_type_keywords.includes(node.label))) &&
                 (userFilter === "All" || user_filter_keys[userFilter].includes(node.label)) &&
                 (permissionsFilter === "All" || permission_filter_keys[permissionsFilter].includes(node.label)) &&
                 (assetsFilter === "All" || assets_filter_keys[assetsFilter].includes(node.label))
              );
            }});
            // Update the network with the filtered nodes and edges
            network.setData({{ nodes: filteredNodes, edges: edges }});
          }}

          // Call redrawAll on initial load
          redrawAll();
        </script>
      </body>
    </html>
    """

    return vis_code
