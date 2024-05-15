{ pkgs, lib, config, inputs, ... }:

{
  packages = with pkgs; [ nodePackages_latest.pyright ];
}
