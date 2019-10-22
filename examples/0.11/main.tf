terraform {
  backend "http" {
    address = "http://localhost:8000/example-0.11"
  }
}

module "foo" {
  source = "./modules/foo"
}

module "bar" {
  source = "./modules/bar"
}

module "baz" {
  source = "./modules/baz"
}

output "foo_content" {
  value = "${module.foo.content}"
}

output "bar_content" {
  value = "${module.bar.content}"
}

output "baz_content" {
  value = "${module.baz.content}"
}
