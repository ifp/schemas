<?php

namespace IFP\Schemas\Fixtures;

class Loader
{
    public function loadFixture($fixture_file, $as_array = true)
    {
        $file_path = dirname(__FILE__) . '/../../json/fixtures/' . $fixture_file .'.json';

        if (file_exists($file_path)) {
            return json_decode(file_get_contents($file_path), $as_array);
        }

        return [];
    }
}
