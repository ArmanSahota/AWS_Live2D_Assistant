import os
import yaml
import json
import chardet

def load_config_from_file(filename):
    """
    Load configuration from a YAML file with robust encoding handling.
    
    Args:
        filename: Path to the config file
        
    Returns:
        Dict: Loaded configuration or None if loading fails
    """
    print(f"Loading config file: {filename}")
    
    if not os.path.exists(filename):
        print(f"Config file not found: {filename}")
        return None
    
    # Try common encodings first
    encodings = ["utf-8", "utf-8-sig", "gbk", "gb2312", "ascii"]
    content = None
    
    for encoding in encodings:
        try:
            with open(filename, "r", encoding=encoding) as file:
                content = file.read()
                print(f"Successfully read file with encoding: {encoding}")
                break
        except UnicodeDecodeError:
            continue
    
    if content is None:
        # Try detecting encoding as last resort
        try:
            with open(filename, "rb") as file:
                raw_data = file.read()
            detected = chardet.detect(raw_data)
            if detected["encoding"]:
                content = raw_data.decode(detected["encoding"])
                print(f"Successfully read file with detected encoding: {detected['encoding']}")
        except Exception as e:
            print(f"Error detecting encoding for config file {filename}: {e}")
            return None
    
    try:
        config = yaml.safe_load(content)
        print(f"Successfully parsed YAML from {filename}")
        
        # Log the loaded configuration for debugging
        print(f"Loaded configuration: {json.dumps(config, indent=2, default=str)}")
        
        return config
    except yaml.YAMLError as e:
        print(f"Error parsing YAML from {filename}: {e}")
        return None

def scan_config_alts_directory():
    """Scan the config_alts directory for YAML files."""
    config_files = ["conf.yaml"]  # default config file
    config_alts_dir = "config_alts"
    
    # Check if the directory exists
    if not os.path.exists(config_alts_dir):
        print(f"Config alternatives directory {config_alts_dir} does not exist")
        return config_files
        
    # Scan the directory for YAML files
    try:
        for root, _, files in os.walk(config_alts_dir):
            for file in files:
                if file.endswith((".yaml", ".yml")):
                    # Only add the file name, not the full path
                    config_files.append(file)
                    print(f"Found config file: {file}")
    except Exception as e:
        print(f"Error scanning config directory: {e}")
        
    return config_files

def main():
    print("=== Testing Configuration Loading ===")
    
    # Test loading the main configuration file
    print("\nLoading main configuration file:")
    main_config = load_config_from_file("conf.yaml")
    
    # Scan for alternative configuration files
    print("\nScanning for alternative configuration files:")
    config_files = scan_config_alts_directory()
    print(f"Found configuration files: {config_files}")
    
    # Test loading each alternative configuration file
    for config_file in config_files:
        if config_file == "conf.yaml":
            continue
        
        print(f"\nLoading alternative configuration file: {config_file}")
        config_path = os.path.join("config_alts", config_file)
        alt_config = load_config_from_file(config_path)

if __name__ == "__main__":
    main()
