variable "counts" {
  default = 1
}

variable "length" {
  default = 10
}

variable "prefix" {
  default = ""
}

locals {
    single_length = var.length + var.counts
    many_length   = var.length * var.counts
    prefix        = var.prefix == "" ? "" : "${var.prefix}/"
}
