module "bar" {
  source = "./dependencies/bar"

  counts  = 5
  length = 15
  prefix = path.module
}

output "content" {
    value = module.bar.content
}
